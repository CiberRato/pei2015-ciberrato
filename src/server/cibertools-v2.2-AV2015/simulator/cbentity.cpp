#include "cbentity.h"
#include <iostream>

cbEntity::cbEntity(cbClient * socket, QObject *parent) : QObject(parent)
{
    this->socket = socket;
}

cbEntity::~cbEntity()
{
}

