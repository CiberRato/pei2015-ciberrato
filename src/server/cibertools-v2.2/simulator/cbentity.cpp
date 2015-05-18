#include "cbentity.h"
#include <iostream>

cbEntity::cbEntity(QTcpSocket * socket) 
{
    this->socket = socket;
}

cbEntity::~cbEntity()
{
}

