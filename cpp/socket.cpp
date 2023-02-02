#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>
#include <thread>
#include <chrono>

//Socket
int sock;
sockaddr_in hint;
// Connection Response
int connectRes;
// Connection Status
bool connected {false};

void reconnect(bool onProgramStart)
{
    // Reconnect the socket if connection has been lost
    while (true)
    {
        // If program is starting there is no need to recreate the socket
        if (!onProgramStart)
        {
            // Socket must be created again if connection is lost
            sock = socket(AF_INET, SOCK_STREAM, 0);
        }
        connectRes = connect(sock, (sockaddr*)&hint, sizeof(sockaddr_in));
        if (connectRes == -1)
        {
            std::cout << "Could not connect to server. Trying again...\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(6000));;
            continue;
        }
        else
        {
            std::cout << "Connection with server successful\n\n";
            connected = true;
            break;
        }
    }
}

void sendMessage()
{
    std::string message {"Hello\r\n"};
    while (true)
    {
        int sendRes = send(sock, message.c_str(), message.size() + 1, 0);
        // Check if it failed
        if (sendRes == -1)
        {
            std::cout << "Could not send to server! Connection lost!\r\n";
            connected = false;
            // Reconnect if connection is lost
            reconnect(false);
            sendRes = send(sock, message.c_str(), message.size() + 1, 0);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(5000));
    }
}

void receiveMessage()
{
    char buf[4096];
    std::string response;
    while (true)
    {
        if (connected)
        {
            // Wait for response
            memset(buf, 0, 4096);
            int bytesReceived = recv(sock, buf, 4096, 0);
            if (bytesReceived == -1)
            {
                std::cout << "There was an error getting response from server\n";
            }
            else{
                // Display response
                response = std::string(buf, bytesReceived);
                if (response.length() > 1)
                {
                    std::cout << "SERVER> " << response << "\r\n";
                }
                else
                {
                    continue;
                }
            }
        }
        else
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(5000));
        }
    }
}

int main()
{
    // Create a socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        std::cerr << "Could not create socket";
        return 1;
    }
    // Create a hint structure for the server we are connecting with
    int port {54000};
    std::string ipAdresss {"127.0.0.1"};

    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, ipAdresss.c_str(), &hint.sin_addr);

    // Connect to the server, if connection fails wait for 8 sec and try again
    std::cout << "Connecting to " << ipAdresss << " at port " << port << "\n\n";

    connectRes = connect(sock, (sockaddr*)&hint, sizeof(sockaddr_in));
    if (connectRes == -1)
    {
        reconnect(true);
    }
    connected = true;
    std::cout << "Started Receive Thread\n";
    std::thread receiveThread(receiveMessage);
    std::cout << "Started Send Thread\n";
    std::thread sendThread(sendMessage);

    receiveThread.join();
    std::cout << "Closed Receive Thread\n";
    sendThread.join();
    std::cout << "Closed Send Thread\n";

    // Close the socket
    close(sock);

    return 0;
}
