%{
#include <stdio.h>
#include <stdlib.h>

int yylex();
int yyerror(char *s);
char id[20];
int value;
%}

%union {
    int ival;
    char iden[20];
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
    Declaration NEWLINE Expression { printf("%d", $3); exit(0); }
;

Declaration: 
    ID EQ NUM { sscanf($1, "%s", id); value = $3; }
;
Expression: 
    ID cmi { 
        if (strcmp($1, id)) {printf("Variable %s is not declared", $1); exit(0);};
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






