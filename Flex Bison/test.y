%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern FILE *yyin;

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
    Declaration NEWLINE Expression { printf("%d", $3); exit(0); }
;

Declaration: 
    ID EQ NUM { sscanf($1, "%s", id); value = $3;}
;
Expression: 
    ID cmi { 
        if (strcmp($1, id)) {printf("Identifier \"%s\" is not declared", $1); exit(0);};
        $$ = $2;
    }
;

cmi: 
    OP_PLUS NUM     { $$ = value + $2; }
|   OP_MINUS NUM    { printf("%d\n", value - $2); 
                      exit(0); }
|   OP_MUL NUM      { $$ = value * $2; }
|   OP_DIV NUM      { if ($2 == 0){printf("Cannot divide by zero"); exit(0);}; 
                      printf("%f\n", value*1.0 / $2); 
                      exit(0); }
;
%%

int yyerror(char *s)
{
    fprintf(stderr, "%s\n", s);
}

int main(int argc, char *argv[])
{
    if (argc == 2){
		yyin = fopen(argv[1], "r");
		if(!yyin){
			fprintf(stderr, "Error reading file %s\n", argv[1]);
			exit(1);
		}
	}
    if (yyparse())
        fprintf(stderr, "Successful parsing.\n");
    else
        fprintf(stderr, "error found.\n");
}






