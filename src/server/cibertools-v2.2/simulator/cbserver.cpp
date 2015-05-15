#include "cbserver.h"
#include <iostream>
using namespace std;

cbServer::cbServer(int port, QObject* parent): QObject(parent)
{
    connect(&server, SIGNAL(newConnection()),
            this, SLOT(acceptConnection()));

    server.listen(QHostAddress::Any, port);
}

cbServer::~cbServer()
{
    server.close();
}

void cbServer::acceptConnection()
{
    client = server.nextPendingConnection();

    connect(client, SIGNAL(readyRead()),
            this, SLOT(startRead()));
}

void cbServer::startRead()
{
    // sample for now
    char buffer[1024] = {0};
    client->read(buffer, client->bytesAvailable());
    cout << buffer << endl;
    client->write("reply", 6);
}