%option noyywrap

%{
#include <stdio.h>

#define YY_DECL int yylex()
#include <string.h>
#include "test.tab.h"

void showError();
%}

whitespace  [ \t]
number      0|[1-9][0-9]*
identifier  [_a-zA-Z][_a-zA-Z0-9]{0,30}

%%
{whitespace}
{identifier}    {sscanf(yytext, "%s", yylval.iden); return(ID);}
{number}        {yylval.ival=atoi(yytext); return(NUM);}

\n              {return(NEWLINE);}
"="             {return(EQ);}
"+"             {return(OP_PLUS);}
"-"             {return(OP_MINUS);}
"*"             {return(OP_MUL);}
"/"             {return(OP_DIV);}
.               {showError(); return *yytext;}

%%

void showError()
{
    printf("Cannot understand");
}
