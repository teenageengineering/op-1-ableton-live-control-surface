##################################################################
# 
#   Copyright (C) 2012 Imaginando, Lda & Teenage Engineering AB
#   
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or any later version.
#  
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   For more information about this license please consult the
#   following webpage: http://www.gnu.org/licenses/gpl-2.0.html
#
##################################################################

import Live
    
from OP1 import OP1

def debug_print(message):
    ' Special function for debug output '
    print message
    
def create_instance(c_instance):
    return OP1(c_instance)
