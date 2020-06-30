%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int yylex();
int yyerror(char *s);
char id[20];
int value;
%}

%union {
    char iden[20];
    int ival;
}

%token NUM 
%token ID 
%token EQ
%token OP_PLUS OP_MINUS OP_MUL OP_DIV
%token NEWLINE

%type<ival> NUM Expression cmi
%type<iden> ID

%start Input
%%

Input:
    | Input Line
;

Line: 
    Declaration Expression { printf("%d", $2); exit(0); }
;

Declaration: 
    ID EQ NUM { sscanf($1, "%s", id); value = $3;}
;
Expression: 
    ID cmi { 
        if (strcmp($1, id)) {printf("Variable \"%s\" is not declared", $1); exit(0);};
        $$ = $2;
    }
;

cmi: 
    OP_PLUS NUM     { $$ = value + $2; }
|   OP_MINUS NUM    { $$ = value - $2; }
|   OP_MUL NUM      { $$ = value * $2; }
|   OP_DIV NUM      { $$ = value / $2; }
;
%%

int yyerror(char *s)
{
    fprintf(stderr, "%s\n", s);
}

int main()
{
    if (yyparse())
        fprintf(stderr, "Successful parsing.\n");
    else
        fprintf(stderr, "error found.\n");
}






