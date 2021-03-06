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

#ifndef CBCLIENT_H
#define CBCLIENT_H

#include <QTcpSocket>
#include <QHostAddress>
#include <qxml.h>

#include "cbparameters.h"
#include "cbgrid.h"
#include "cblab.h"

/**
 * base class of all representations of clients in the simulator.
 * 
 *@author Nuno Lau, Artur Pereira & Andreia Melo, Miguel Rodrigues
 */

class cbClient : public QTcpSocket
{
public:
	cbClient();
	virtual ~cbClient();

	bool Reply(cbParameters *param = NULL, cbGrid *grid = NULL, cbLab *lab = NULL);
	bool Refuse();

	bool send(const char *, unsigned int);
};

#endif
