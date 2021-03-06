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

#include "cbclient.h"

#include <QHostAddress>
#include <iostream>
#include <stdio.h>

using std::cerr;

#define REPLYMAXSIZE 8192

cbClient::cbClient() : QTcpSocket()
{
}

cbClient::~cbClient()
{
}

/*!
	Send the OK reply message to client.
*/
bool cbClient::Reply(cbParameters *param, cbGrid *grid, cbLab *lab)
{
    //cout.form("Sending reply for client to %s:%hd\n", a.toString().toLatin1().constData(), p);
	/* constructing reply message */
	char reply[REPLYMAXSIZE];
	int cnt;
	cnt = sprintf(reply, "<Reply Status=\"Ok\">\n\t");
	if (param != NULL) cnt += param->toXml(reply+cnt, REPLYMAXSIZE-cnt);
	if (lab != NULL) cnt += lab->toXml(reply+cnt, REPLYMAXSIZE-cnt);
	if (grid != NULL) cnt += grid->toXml(reply+cnt, REPLYMAXSIZE-cnt);
	cnt += sprintf(reply+cnt, "</Reply>\n");
	cnt += sprintf(reply+cnt, "\x04");

    /* send reply to client */
    if (write(reply) != cnt)
	{
		cerr << "Fail replying to client\n";
		return false;
    }
	return true;
}

/*!
	Send the Refused reply message to client.
*/
bool cbClient::Refuse()
{
	//cout.form("Sending refuse for client to %s:%hd\n", a.toString().latin1(), p);
	/* set peer address and peer port */

	/* constructing reply message */
	char reply[256];
	int cnt;
	cnt = sprintf(reply, "<Reply Status=\"Refused\"></Reply>\n");
	cnt += sprintf(reply+cnt, "\x04");

    /* send reply to client */
    if (write(reply) != cnt)
	{
		cerr << "Fail replying to client\n";
		return false;
    }
	return true;
}


/*!
	Send xml message to client.
*/
bool cbClient::send(const char *xml, unsigned int cnt)
{
	char reply[cnt+1];
	strcpy(reply, xml);
	
	cnt += sprintf(reply+cnt, "\x04");

	if (write(reply) != (int)cnt)
    {
        cerr << "Fail sending xml message to client\n";
		return false;
    }
	return true;
}
