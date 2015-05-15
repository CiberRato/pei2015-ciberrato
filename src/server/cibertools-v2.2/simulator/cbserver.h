#ifndef _CB_SERVER_
#define _CB_SERVER_

#include <QtNetwork>
#include <QObject>
#include <QTcpServer>
#include <QTcpSocket>

class cbServer: public QObject
{
	Q_OBJECT
public:
	cbServer(int port, void (*onAccept)(), QObject * parent = 0);
	~cbServer();
public slots:
	void acceptConnection();
	void startRead();
protected:
	QTcpServer server;
	QTcpSocket* client;
};

#endif