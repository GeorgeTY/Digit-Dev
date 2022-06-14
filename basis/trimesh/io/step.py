import numpy as np

import networkx as nx
import itertools

from collections import deque
from tempfile import NamedTemporaryFile
from distutils.spawn import find_executable
from subprocess import check_call
from xml.etree import cElementTree

from ..constants import res, log

_METERS_TO_INCHES = 1.0 / .0254
_STEP_FACETER = find_executable('export_product_asm')


def load_step(file_obj, file_type=None):
    '''
    Use the STEPtools Inc. Author Tools binary to mesh a STEP file,
    and return a list of Trimesh objects.

    Using this over openCASCADE as it is signifigantly more stable (though not OSS.) 
    
    STEPtools Inc. provides the binary under this license:
    http://www.steptools.com/demos/license_author.html

    To install the required binary ('export_product_asm') into PATH:
        wget http://www.steptools.com/demos/stpidx_author_linux_x86_64_16.0.zip
        unzip stpidx_author_linux_x86_64_16.0.zip
        sudo cp stpidx_author_linux_x86_64/bin/export_product_asm /usr/bin/
    
    Arguments
    ----------
    file_obj:  file like object containing step file
    file_type: unused

    Returns
    ----------
    meshes: list of Trimesh objects (with correct metadata set from STEP file)
    '''

    with NamedTemporaryFile() as out_file:
        with NamedTemporaryFile(suffix='.STEP') as in_file:
            if hasattr(file_obj, 'read'):
                in_file.write(file_obj.read())
                in_file.seek(0)
                file_name = in_file.name
            else:
                file_name = file_obj
            check_call([_STEP_FACETER, file_name,
                        '-tol', str(res.mesh),
                        '-o', out_file.name])
            t = cElementTree.parse(out_file)
    meshes = {}
    # get the meshes without metadata from the XML document
    for shell in t.findall('shell'):
        # query the xml structure for vertices and faces
        vertices = np.array([v.get('p').split() for v in shell.findall('.//v')],
                            dtype=np.float)
        faces = np.array([f.get('v').split() for f in shell.findall('.//f')],
                         dtype=np.int)
        # normals aren't always returned but faces have correct winding
        # so they are autogenerated correctly from dot products
        mesh = {'vertices': vertices,
                'faces': faces,
                'metadata': {}}
        # store the mesh by id reference
        meshes[shell.get('id')] = mesh

    try:
        # populate the graph of shapes and transforms
        g = nx.MultiDiGraph()
        # keys: {mesh id : shape id}
        mesh_shape = {}
        # assume that the document has consistant units
        to_inches = None
        for shape in t.findall('shape'):
            shape_id = shape.get('id')
            shape_unit = shape.get('unit')
            mesh_id = shape.get('shell')
            if not shape_unit is None:
                to_inches = float(shape_unit.split()[1]) * _METERS_TO_INCHES
            if not mesh_id is None:
                for i in mesh_id.split():
                    mesh_shape[i] = shape_id
                # g.node[shape_id]['mesh'] = mesh_id

                g.add_node(shape_id, {'mesh': mesh_id})

            for child in shape.getchildren():
                child_id = child.get('ref')
                transform = np.array(child.get('xform').split(),
                                     dtype=np.float).reshape((4, 4)).T
                g.add_edge(shape_id, child_id, transform=transform)

        # which product ID has the root shape
        prod_root = t.getroot().get('root')
        shape_root = None
        for prod in t.findall('product'):
            prod_id = prod.get('id')
            prod_name = prod.get('name')
            prod_shape = prod.get('shape')
            if prod_id == prod_root:
                shape_root = prod_shape
            g.node[prod_shape]['product_name'] = prod_name

            # now that the assembly tree has been populated, traverse it to
        # find the final transforms and quantities for the meshes we extracted
        for mesh_id in meshes.keys():
            shape_id = mesh_shape[mesh_id]
            transforms_all = deque()
            path_str = deque()
            if shape_id == shape_root:
                paths = [[shape_id, shape_id]]
            else:
                paths = nx.all_simple_paths(g, shape_root, shape_id)
            paths = np.array(list(paths))
            garbage, unique = np.unique(['.'.join(i) for i in paths], return_index=True)
            paths = paths[unique]
            for path in paths:
                path_name = [g.node[i]['product_name'] for i in path[:-1]]
                edges = np.column_stack((path[:-1],
                                         path[:-1])).reshape(-1)[1:-1].reshape((-1, 2))
                transforms = [np.eye(4)]
                for e in edges:
                    # get every transform from the edge
                    local = [i['transform'] for i in g.edge[e[0]][e[1]].values()]
                    # all the transforms are sequential, so we want combinations
                    transforms = [np.dot(*i) for i in itertools.product(transforms, local)]

                transforms_all.extend(transforms)
                path_str.extend(['/'.join(path_name)] * len(transforms))
            meshes[mesh_id]['vertices'] *= to_inches
            meshes[mesh_id]['metadata']['units'] = 'inches'
            meshes[mesh_id]['metadata']['name'] = path_name[-1]
            meshes[mesh_id]['metadata']['paths'] = np.array(path_str)
            meshes[mesh_id]['metadata']['quantity'] = len(transforms_all)
            meshes[mesh_id]['metadata']['transforms'] = np.array(transforms_all)
    except:
        log.error('STEP load processing error, aborting metadata!', exc_info=True)

    return meshes.values()


if _STEP_FACETER is None:
    log.debug('STEP loading unavailable!')
    _step_loaders = {}
else:
    _step_loaders = {'step': load_step,
                     'stp': load_step}
