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

#include "cbpanel.h"

#include <QTcpSocket>
#include <QHostAddress>

#include <iostream>
#include "cbpanelhandler.h"

using namespace std;

cbPanel::cbPanel(QTcpSocket * client) : cbClient(client)
{
}

cbPanel::~cbPanel()
{
}

bool cbPanel::readCommand(cbPanelCommand *command)
{
    /* look for an incoming message */
    //char xmlBuff[1024*32];
    //int xmlSize;

    //if (!hasPendingDatagrams())
    //    return false;

    QByteArray xmlBuff = client->readAll();
    /*if ((xmlSize=readDatagram(xmlBuff, 1024*32-1)) < 0)
    {
        cerr << "Error reading from Viewer Socket - " << errorString().toStdString();
        return false;
    }
    else xmlBuff[xmlSize]='\0';*/

#ifdef DEBUG_VIEW
    cerr << "cbPanel: " << xmlBuff << endl;
#endif

    /* parse xml message */
    source.setData(xmlBuff);
    cbPanelHandler *handler = new cbPanelHandler(QString(xmlBuff));
    parser.setContentHandler(handler);
    if (!parser.parse(source))
    {
        cerr << "cbPanel::Fail parsing xml view message\n";
        return false;
    }
    *command = handler->Command();
    return true;
}
