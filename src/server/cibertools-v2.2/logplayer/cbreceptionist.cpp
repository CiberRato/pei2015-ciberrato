/*
    This file is part of ciberRatoToolsSrc.

    Copyright (C) 2001-2011 Universidade de Aveiro

    ciberRatoToolsSrc is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    ciberRatoToolsSrc is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/
/*
	cbReceptionist

*/

#include "cbreceptionist.h"

#include "cbreceptionform.h"
#include "cbreceptionhandler.h"

#include <qhostaddress.h>
#include <qmessagebox.h>
#include <qstring.h>
#include <qxml.h>
//#include <q3dict.h>

#include <string.h>

#ifndef MicWindows
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
//#else
//#include <WinSock2.h>
#endif

#include <stdlib.h>

using std::cerr;
using std::cout;

/*!
	Create socket and bind it with machine address and given port.
	Set the socket non-blocking.
*/
cbReceptionist::cbReceptionist()
{
	xmlParser = 0;
	status = true;
}

/*!	
	Does nothing.
*/
cbReceptionist::~cbReceptionist()
{
}

/*!
	Returns true if internal status is bad, and returns false if it is good.
*/
bool cbReceptionist::bad(void)
{
	return status == false;
}


/*!
	Set the xml parser.
*/
void cbReceptionist::setXmlParser(QXmlSimpleReader *parser)
{
	xmlParser = parser;
	
}


///*!
//	Set the xml source.
//*/
//void cbReceptionist::setXmlSource(QXmlInputSource *source)
//{
//	xmlSource = source;
//}
//
//
/*!
	Check input port for an incoming xml message.
	If one, parse it, fill in the check-in form and return true;
	Otherwise returns false.
*/
bool cbReceptionist::CheckIn(QTcpSocket* client)
{
	/* check if parser is set */
	if (xmlParser == 0) 
	{
        cerr << "Parser was not setup\n";
        QMessageBox::critical(0,"Error",
                              "Error in parser",
                              QMessageBox::Ok, Qt::NoButton, Qt::NoButton);
        exit (1);
	}
	
	QByteArray readArr, datagram;
	while (strcmp((readArr = client->read(1)).data(), "\x04") != 0) {
        if (readArr.isEmpty()) {
            return false;
        }
        datagram += readArr;
    }

	/* parse xml message */
	cbReceptionHandler handler(xmlParser, client);
	if (!handler.parse(datagram.data()))
	{
		cerr << "Fail parsing xml message\n" << datagram.data() << "\n";
		return false;
	}

	switch (handler.objectType())
	{
		case cbReceptionHandler::VIEW:
			form.type = cbClientForm::VIEW;
			form.client.view = handler.viewObject();
			cout << "View is requesting registration\n";
			break;
		case cbReceptionHandler::PANEL:
			form.type = cbClientForm::PANEL;
			form.client.panel = handler.panelObject();
			cout << "Panel is requesting registration\n";
			break;
		default:
			form.type = cbClientForm::UNKNOWN;
			break;
	}
	return true;
}

/*!
	Returns the last filled check-in (client) form.
*/
cbClientForm &cbReceptionist::Form()
{
	return form;
}
