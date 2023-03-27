################################################################################
# This software is being provided under the Creative Commons                   #
# Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)  #
# license. For more information about the restrictions associated with this    #
# license, see                                                                 #
#                                                                              #
#   https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode                #
#                                                                              #
# The information provided by this notebook does not contain specific legal    #
# advice and use of this information does not create an attorney-client        #
# relationship with BNH.AI.                                                    #
################################################################################

import sys
import traceback

def html_error_message(exception: Exception=None, stack_trace: bool=True, context: str=""):
    html = ''
    if context != "":
        error_message_html=f'<div style="color:#FF0000;font-weight:bold">{context}: {exception}</div>'
    else:
        error_message_html=f'<div style="color:#FF0000;font-weight:bold">An error occurred when attempting to execute this Jupyter notebook: {exception}</div>'
    stack_trace_html = ''
    if stack_trace:
        limit = None
        type, value, tb = sys.exc_info(  )
        list = traceback.format_tb(tb, limit) + traceback.format_exception_only(type, value)
        stack_trace_html = '<pre style="color:#87CEEB;">Traceback (innermost last):\n' + '%-20s %s' % ( "".join(list[:-1]), list[-1] ) + '</pre>' 
        html = f"<br><br>{error_message_html}<br>{stack_trace_html}"
    else:
        html = f"<br><br>{error_message_html}"
    return html


