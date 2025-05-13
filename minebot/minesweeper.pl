:- dynamic cell/3.

% Valid coordinate bounds
valid_coord(X,Y) :-
    integer(X), integer(Y),
    X >= 0, X =< 9,
    Y >= 0, Y =< 22.

% Safe neighbor logic
neighbor(X,Y,NX,NY) :-
    number(X), number(Y),
    between(-1,1,DX), between(-1,1,DY),
    (DX \= 0 ; DY \= 0),
    NX is X + DX, NY is Y + DY.

safe_hidden_neighbor(X,Y,NX,NY) :-
    number(X), number(Y),
    neighbor(X,Y,NX,NY),
    valid_coord(NX,NY),
    cell(NX,NY,hidden).

safe_flagged_neighbor(X,Y,NX,NY) :-
    number(X), number(Y),
    neighbor(X,Y,NX,NY),
    valid_coord(NX,NY),
    cell(NX,NY,flagged).

count(Pred,N) :-
    findall(1, Pred, L),
    length(L, N).

% Rule A
action(flag(X2,Y2)) :-
    cell(X,Y,number(N)),
    findall(1, safe_flagged_neighbor(X,Y,_,_), L1), length(L1, F),
    findall(1, safe_hidden_neighbor(X,Y,_,_), L2), length(L2, U),
    N =:= F + U,
    safe_hidden_neighbor(X,Y,X2,Y2).

% Rule B
action(click(X2,Y2)) :-
    cell(X,Y,number(N)),
    findall(1, safe_flagged_neighbor(X,Y,_,_), L1), length(L1, F),
    N =:= F,
    safe_hidden_neighbor(X,Y,X2,Y2).

% Rule C: number(0) → reveal all neighbors
action(click(X2,Y2)) :-
    cell(X,Y,number(0)),
    safe_hidden_neighbor(X,Y,X2,Y2).

% Rule D: fallback guess
action(guess(X,Y)) :-
    cell(X,Y,hidden),
    number(X), number(Y),
    format('Guessing cell: (~w,~w)~n', [X,Y]).

% Force rule logging
next_action(A) :- action(flag(X,Y)),  A = flag(X,Y),  writeln(A), !.
next_action(A) :- action(click(X,Y)), A = click(X,Y), writeln(A), !.
next_action(A) :- action(guess(X,Y)), A = click(X,Y), writeln(A), !.
next_action(no_move) :-
    writeln('No safe moves deduced from current state'), fail.
