#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

int main()
{
    int sockfd;
    int client_sockfd;
    struct sockaddr_in addr;

    socklen_t len = sizeof(struct sockaddr_in);
    struct sockaddr_in from_addr;

    char buf[1024];

    // Receive buffer initialization
    memset(buf, 0, sizeof(buf));

    // Socket generation
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket");
    }

    // Stand-by IP / port number setting
    addr.sin_family = AF_INET;
    addr.sin_port = htons(1234);
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

    // Receive
    int rsize;
    while (1)
    {
        rsize = recv(client_sockfd, buf, sizeof(buf), 0);

        if (rsize == 0)
        {
            break;
        }
        else if (rsize == -1)
        {
            perror("recv");
        }
        else
        {
            printf("receive:%s\n", buf);
            sleep(1);

            // response
            printf("send:%s\n", buf);
            write(client_sockfd, buf, rsize);
        }
    }

    // Socket closed
    close(client_sockfd);
    close(sockfd);

    return 0;
}
