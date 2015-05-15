#include <QtNetwork>
#include <QObject>
#include <QTcpServer>
#include <QTcpSocket>

class cbServer: public QObject
{
	Q_OBJECT
public:
	cbServer(int port, QObject * parent = 0);
	~cbServer();
public slots:
	void acceptConnection();
	void startRead();
protected:
	QTcpServer server;
	QTcpSocket* client;
};