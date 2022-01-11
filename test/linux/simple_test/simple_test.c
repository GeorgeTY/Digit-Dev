/** \file
 * \brief Example code for Simple Open EtherCAT master
 *
 * Usage : simple_test [ifname1]
 * ifname is NIC interface, f.e. eth0
 *
 * This is a minimal test.
 *
 * (c)Arthur Ketels 2010 - 2011
 */

#include <stdio.h>
#include <string.h>
#include <inttypes.h>

#include "ethercat.h"

#define EC_TIMEOUTMON 500

char IOmap[4096];
OSAL_THREAD_HANDLE thread1;
int expectedWKC;
boolean needlf;
volatile int wkc;
boolean inOP;
uint8 currentgroup = 0;

void simpletest(char *ifname)
{
   int i;
   needlf = FALSE;
   inOP = FALSE;

   printf("Starting simple test\n");

   /* initialise SOEM, bind socket to ifname */
   if (ec_init(ifname))
   {
      printf("ec_init on %s succeeded.\n", ifname);
      /* find and auto-config slaves */

      if (ec_config_init(FALSE) > 0)
      {
         printf("%d slaves found and configured.\n", ec_slavecount);

         ec_slave[1].CoEdetails &= ~ECT_COEDET_SDOCA;

         /* Detect slave ATI EtherCAT OEM from vendor ID and product code */
         if ((ec_slave[1].eep_man == 0x00000732) && (ec_slave[1].eep_id == 0x26483052))
         {
            printf("Found %s at position %d, ID: %x\n", ec_slave[1].name, ec_slave[1].eep_id, 1);
         }
         else
         {
         }

         /* Manually set SMs for ATI OEM Board*/
         ec_slave[1].SM[2].StartAddr = htoes(0x1800);
         ec_slave[1].SM[2].SMlength = htoes(0x0008);
         ec_slave[1].SM[2].SMflags = htoel(0x00010064);
         ec_slave[1].SMtype[2] = 3;

         ec_slave[1].SM[3].StartAddr = htoes(0x1c00);
         ec_slave[1].SM[3].SMlength = htoes(0x0020);
         ec_slave[1].SM[3].SMflags = htoel(0x00010020);
         ec_slave[1].SMtype[3] = 4;
         /* Setting end*/

         ec_config_map(&IOmap);

         ec_configdc();

         printf("Slaves mapped, state to SAFE_OP.\n");

         ec_slave[1].state = EC_STATE_SAFE_OP;
         ec_writestate(1);

         /* wait for all slaves to reach SAFE_OP state */
         ec_statecheck(0, EC_STATE_SAFE_OP, EC_TIMEOUTSTATE * 3);

         if (ec_slave[0].state == EC_STATE_SAFE_OP)
         {
            printf("Safe-OP state reached for all slaves.\n");

            int32_t Fx, Fy, Fz, Tx, Ty, Tz;
            int32_t data[6];
            int rdl = 4 * 6, rdlu = 2 * 2;
            uint8 Units[2];

            ec_SDOread(1, 0x2040, 0x29, FALSE, &rdlu, &Units[0], EC_TIMEOUTRXM); //1 Lbf  2 N  3 Klbf  4 kN  5 Kg
            ec_SDOread(1, 0x2040, 0x2a, FALSE, &rdlu, &Units[1], EC_TIMEOUTRXM); //1 Lbf-in  2 Lbf-ft  3 N-m  4 N-mm  5 Kg-cm  6 kN-m
            printf("Force Units: %d ,Torque Units: %d\n", Units[0], Units[1]);
            for (i = 1; i <= 1000; i++)
            {
               ec_send_processdata();
               ec_receive_processdata(EC_TIMEOUTRET);
               ec_SDOread(1, 0x6000, 0x01, TRUE, &rdl, &data, EC_TIMEOUTRXM);
               // ec_SDOread(1, 0x6000, 0x02, FALSE, &rdl, &Fy, EC_TIMEOUTRXM);
               // ec_SDOread(1, 0x6000, 0x03, FALSE, &rdl, &Fz, EC_TIMEOUTRXM);
               // ec_SDOread(1, 0x6000, 0x04, FALSE, &rdl, &Tx, EC_TIMEOUTRXM);
               // ec_SDOread(1, 0x6000, 0x05, FALSE, &rdl, &Ty, EC_TIMEOUTRXM);
               // ec_SDOread(1, 0x6000, 0x06, FALSE, &rdl, &Tz, EC_TIMEOUTRXM);
               Fx = data[0];
               Fy = data[1];
               Fz = data[2];
               Tx = data[3];
               Ty = data[4];
               Tz = data[5];
               // printf("No.%d Fx: %.5f Fy: %.5f Fz: %.5f Tx: %.5f Ty: %.5f Tz: %.5f\n",
               //        i, (double)Fx / 1000000, (double)Fy / 1000000, (double)Fz / 1000000, (double)Tx / 1000000, (double)Ty / 1000000, (double)Tz / 1000000);
               printf("%d,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f\n",
                      i, (double)Fx / 1000000, (double)Fy / 1000000, (double)Fz / 1000000, (double)Tx / 1000000, (double)Ty / 1000000, (double)Tz / 1000000);
               getchar();
            }
            osal_usleep(5000);
         }

         else
         {
            printf("Not all slaves reached operational state.\n");
            ec_readstate();
            for (i = 1; i <= ec_slavecount; i++)
            {
               if (ec_slave[i].state != EC_STATE_OPERATIONAL)
               {
                  printf("Slave %d State=0x%2.2x StatusCode=0x%4.4x : %s\n",
                         i, ec_slave[i].state, ec_slave[i].ALstatuscode, ec_ALstatuscode2string(ec_slave[i].ALstatuscode));
               }
            }
         }
         printf("\nRequest init state for all slaves\n");
         ec_slave[0].state = EC_STATE_INIT;
         /* request INIT state for all slaves */
         ec_writestate(0);
      }
      else
      {
         printf("No slaves found!\n");
      }
      printf("End simple test, close socket\n");
      /* stop SOEM, close socket */
      ec_close();
   }
   else
   {
      printf("No socket connection on %s\nExcecute as root\n", ifname);
   }
}

OSAL_THREAD_FUNC ecatcheck(void *ptr)
{
   int slave;
   (void)ptr; /* Not used */

   while (1)
   {
      if (inOP && ((wkc < expectedWKC) || ec_group[currentgroup].docheckstate))
      {
         if (needlf)
         {
            needlf = FALSE;
            printf("\n");
         }
         /* one ore more slaves are not responding */
         ec_group[currentgroup].docheckstate = FALSE;
         ec_readstate();
         for (slave = 1; slave <= ec_slavecount; slave++)
         {
            if ((ec_slave[slave].group == currentgroup) && (ec_slave[slave].state != EC_STATE_OPERATIONAL))
            {
               ec_group[currentgroup].docheckstate = TRUE;
               if (ec_slave[slave].state == (EC_STATE_SAFE_OP + EC_STATE_ERROR))
               {
                  printf("ERROR : slave %d is in SAFE_OP + ERROR, attempting ack.\n", slave);
                  ec_slave[slave].state = (EC_STATE_SAFE_OP + EC_STATE_ACK);
                  ec_writestate(slave);
               }
               else if (ec_slave[slave].state == EC_STATE_SAFE_OP)
               {
                  printf("WARNING : slave %d is in SAFE_OP, change to OPERATIONAL.\n", slave);
                  ec_slave[slave].state = EC_STATE_OPERATIONAL;
                  ec_writestate(slave);
               }
               else if (ec_slave[slave].state > EC_STATE_NONE)
               {
                  if (ec_reconfig_slave(slave, EC_TIMEOUTMON))
                  {
                     ec_slave[slave].islost = FALSE;
                     printf("MESSAGE : slave %d reconfigured\n", slave);
                  }
               }
               else if (!ec_slave[slave].islost)
               {
                  /* re-check state */
                  ec_statecheck(slave, EC_STATE_OPERATIONAL, EC_TIMEOUTRET);
                  if (ec_slave[slave].state == EC_STATE_NONE)
                  {
                     ec_slave[slave].islost = TRUE;
                     printf("ERROR : slave %d lost\n", slave);
                  }
               }
            }
            if (ec_slave[slave].islost)
            {
               if (ec_slave[slave].state == EC_STATE_NONE)
               {
                  if (ec_recover_slave(slave, EC_TIMEOUTMON))
                  {
                     ec_slave[slave].islost = FALSE;
                     printf("MESSAGE : slave %d recovered\n", slave);
                  }
               }
               else
               {
                  ec_slave[slave].islost = FALSE;
                  printf("MESSAGE : slave %d found\n", slave);
               }
            }
         }
         if (!ec_group[currentgroup].docheckstate)
            printf("OK : all slaves resumed OPERATIONAL.\n");
      }
      osal_usleep(10000);
   }
}

int main(int argc, char *argv[])
{
   if (argc > 1)
   {
      /* create thread to handle slave error handling in OP */
      //      pthread_create( &thread1, NULL, (void *) &ecatcheck, (void*) &ctime);
      osal_thread_create(&thread1, 128000, &ecatcheck, (void *)&ctime);
      /* start cyclic part */
      simpletest(argv[1]);
   }
   else
   {
      printf("Usage: simple_test ifname1\nifname = eth0 for example\n");
   }
   return (0);
}
