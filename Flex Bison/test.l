%option noyywrap

%{
#include <stdio.h>

#define YY_DECL int yylex()
#include <string.h>
#include "test.tab.h"

void showError();
%}

number      [0-9]+
identifier  ^[^\d\W]\w*

%%

{number}        {yylval.ival=atoi(yytext); return(NUM);}
{identifier}    {sscanf(yytext, "%s", yylval.iden); return(ID);}

\n		        {return NEWLINE;}
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
