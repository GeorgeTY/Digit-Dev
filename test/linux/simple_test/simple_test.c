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
#include <time.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include "ethercat.h"

#define EC_TIMEOUTMON 500
#define PRE_CALIBRATION

char IOmap[4096];
OSAL_THREAD_HANDLE thread1;
int expectedWKC;
boolean needlf;
volatile int wkc;
boolean inOP;
uint8 currentgroup = 0;
int32_t FT_data[6];

char buf[1024];

void simpletest(char *ifname)
{
   int i;
   needlf = FALSE;
   inOP = FALSE;
   // time_t now;
   struct timeval now;

   printf("Starting simple test\n");

   /* Start Socket*/
   int sockfd;
   int client_sockfd;
   struct sockaddr_in addr;

   socklen_t len = sizeof(struct sockaddr_in);
   struct sockaddr_in from_addr;

   // Receive buffer initialization
   memset(buf, 0, sizeof(buf));

   // Socket generation
   if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
   {
      perror("socket");
   }

   // Stand-by IP / port number setting
   addr.sin_family = AF_INET;
   addr.sin_port = htons(6319);
   addr.sin_addr.s_addr = INADDR_ANY;

   // bind
   if (bind(sockfd, (struct sockaddr *)&addr, sizeof(addr)) < 0)
   {
      perror("bind");
   }

   printf("waiting for client's connection..\n");
   // Waiting for reception
   if (listen(sockfd, SOMAXCONN) < 0)
   {
      perror("listen");
   }

   // Waiting for a connect request from a client
   if ((client_sockfd = accept(sockfd, (struct sockaddr *)&from_addr, &len)) < 0)
   {
      perror("accept");
   }
   /* End Config */

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
            printf("Found %s at position %d, ID: %x\n", ec_slave[1].name, 1, ec_slave[1].eep_id);
         }
         else
         {
            printf("ERROR: ATI Sensor NOT FOUND or misconfigured.");
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
            int32_t Pre_Fx = 0, Pre_Fy = 0, Pre_Fz = 0, Pre_Tx = 0, Pre_Ty = 0, Pre_Tz = 0;
            int32_t Last_Fx;
            int rdl = 4 * 6, rdlu = 2 * 2;
            uint8 Units[2];

            ec_SDOread(1, 0x2040, 0x29, FALSE, &rdlu, &Units[0], EC_TIMEOUTRXM); // 1 Lbf  2 N  3 Klbf  4 kN  5 Kg
            ec_SDOread(1, 0x2040, 0x2a, FALSE, &rdlu, &Units[1], EC_TIMEOUTRXM); // 1 Lbf-in  2 Lbf-ft  3 N-m  4 N-mm  5 Kg-cm  6 kN-m
            printf("Force Units: %d ,Torque Units: %d\n", Units[0], Units[1]);

// Pre-Calibration(Zeroing)
#ifdef PRE_CALIBRATION
            printf("Calibrating, Do not add extra load to the Sensor!\n\n");
            i = 1;
            do
            {
               ec_send_processdata();
               ec_receive_processdata(EC_TIMEOUTRET);
               ec_SDOread(1, 0x6000, 0x01, TRUE, &rdl, &FT_data, EC_TIMEOUTRXM);

               if (Last_Fx != FT_data[0])
               {
                  Pre_Fx += FT_data[0];
                  Pre_Fy += FT_data[1];
                  Pre_Fz += FT_data[2];
                  Pre_Tx += FT_data[3];
                  Pre_Ty += FT_data[4];
                  Pre_Tz += FT_data[5];

                  i++;
               }
               Last_Fx = FT_data[0];
            } while (i <= 10);

            Pre_Fx = Pre_Fx / 10;
            Pre_Fy = Pre_Fy / 10;
            Pre_Fz = Pre_Fz / 10;
            Pre_Tx = Pre_Tx / 10;
            Pre_Ty = Pre_Ty / 10;
            Pre_Tz = Pre_Tz / 10;
#endif
            // Send Operational-Got to Client
            strcpy(buf, "OPGT");
            write(client_sockfd, buf, sizeof(buf));
            int rsize;

            // printf("Data coming! Press ENTER to continue.\n\n");
            for (i = 1; i <= 1000; i++)
            {
               memset(buf, 0, strlen(buf));
               rsize = recv(client_sockfd, buf, sizeof(buf), 0);
               printf("recved: %d\n", rsize);

               if (rsize == 0)
               {
                  printf("rsize = 0");
                  // return;
               }
               else if (rsize == -1)
               {
                  perror("recv");
               }
               else
               {
                  printf("recv: %s\n", buf);
                  if (strcmp(buf, "REQD") == 0)
                  {
                     printf("Getting Data\n");
                     do
                     {
                        ec_send_processdata();
                        ec_receive_processdata(EC_TIMEOUTRET);
                        ec_SDOread(1, 0x6000, 0x01, TRUE, &rdl, &FT_data, EC_TIMEOUTRXM);
                        // ec_SDOread(1, 0x6000, 0x02, FALSE, &rdl, &Fy, EC_TIMEOUTRXM);
                        // ec_SDOread(1, 0x6000, 0x03, FALSE, &rdl, &Fz, EC_TIMEOUTRXM);
                        // ec_SDOread(1, 0x6000, 0x04, FALSE, &rdl, &Tx, EC_TIMEOUTRXM);
                        // ec_SDOread(1, 0x6000, 0x05, FALSE, &rdl, &Ty, EC_TIMEOUTRXM);
                        // ec_SDOread(1, 0x6000, 0x06, FALSE, &rdl, &Tz, EC_TIMEOUTRXM);
                        gettimeofday(&now, NULL);
                        usleep(1000);
                        printf("Loop\n");
                     } while (FT_data[0] == Last_Fx); // Avoid stuck

                     Fx = FT_data[0];
                     Fy = FT_data[1];
                     Fz = FT_data[2];
                     Tx = FT_data[3];
                     Ty = FT_data[4];
                     Tz = FT_data[5];

                     Last_Fx = FT_data[0];

                     // Send to Client
                     sprintf(buf, "%.5f", (Fz - Pre_Fz) / 1000000.0);
                     write(client_sockfd, buf, sizeof(buf));
                     printf("Printed to Socket: %s\n", buf);

                     // printf("No.%d Fx: %.5f Fy: %.5f Fz: %.5f Tx: %.5f Ty: %.5f Tz: %.5f\n",
                     //        i, (double)Fx / 1000000, (double)Fy / 1000000, (double)Fz / 1000000,
                     //        (double)Tx / 1000000, (double)Ty / 1000000, (double)Tz / 1000000);
                     // printf("%ld,%ld,%d,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f\n",
                     //        now.tv_sec, now.tv_usec, i,
                     //        (double)(Fx - Pre_Fx) / 1000000, (double)(Fy - Pre_Fy) / 1000000, (double)(Fz - Pre_Fz) / 1000000,
                     //        (double)(Tx - Pre_Tx) / 1000000, (double)(Ty - Pre_Ty) / 1000000, (double)(Tz - Pre_Tz) / 1000000);
                     printf("%d,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f\n",
                            i,
                            (double)(Fx - Pre_Fx) / 1000000, (double)(Fy - Pre_Fy) / 1000000, (double)(Fz - Pre_Fz) / 1000000,
                            (double)(Tx - Pre_Tx) / 1000000, (double)(Ty - Pre_Ty) / 1000000, (double)(Tz - Pre_Tz) / 1000000);
                     // getchar();
                     osal_usleep(5000);
                  }
                  else
                  {
                     printf("Not REQD\n");
                  }
               }
            }

            osal_usleep(5000);
         }

         else
         {
            printf("\nRetry! Not all slaves reached operational state.\n\n");
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

      strcpy(buf, "OPFL");
      write(client_sockfd, buf, sizeof(buf));

      /* stop SOEM, close socket */
      ec_close();

      close(client_sockfd);
      close(sockfd);
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
