#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>

int main()
{
    // Create a socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        std::cerr << "Could not create socket";
        return 1;
    }
    // Create a hint structure for the server we are connecting with
    int port = 54000;
    std::string ipAdresss = "127.0.0.1";

    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, ipAdresss.c_str(), &hint.sin_addr);

    // Connect to the server on the socket
    int connectRes = connect(sock, (sockaddr*)&hint, sizeof(sockaddr_in));
    if (connectRes == -1)
    {
        return 1;
    }

    char buf[4096];
    std::string userInput;

    while (true){
        // Enter lines of text
        std::cout << "> ";
        getline(std::cin, userInput);

        // Send to server
        int sendRes = send(sock, userInput.c_str(), userInput.size() + 1, 0);
        // Check if it failed
        if (sendRes == -1)
        {
            std::cout << "Could not send to server! Whoops!\r\n";
            continue;
        }

        // Wait for response
        memset(buf, 0, 4096);
        int bytesReceived = recv(sock, buf, 4096, 0);
        if (bytesReceived == -1)
        {
            std::cout << "There was an error getting response from server";
        }
        else{
            // Display response
            std::cout << "SERVER> " << std::string(buf, bytesReceived) << "\r\n";
        }

    }

    // Close the socket
    close(sock);

    return 0;
}
