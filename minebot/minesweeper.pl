:- dynamic     cell/3.
:- multifile   cell/3.
:- discontiguous action/1.

:- use_module(library(clpfd)).
:- use_module(library(lists)).

neighbor(X,Y,NX,NY) :-
    between(-1,1,DX), between(-1,1,DY),
    (DX =\= 0 ; DY =\= 0),
    NX is X+DX, NY is Y+DY,
    cell(NX,NY,_).

safe_hidden_neighbor(X,Y,NX,NY) :-
    neighbor(X,Y,NX,NY),
    cell(NX,NY,hidden).

safe_flagged_neighbor(X,Y,NX,NY) :-
    neighbor(X,Y,NX,NY),
    cell(NX,NY,flagged).

count(Pred,N) :- findall(1,Pred,L), length(L,N).


% Rule A: Classic all hidden = mines
action(flag(X2,Y2)) :-
    cell(X,Y,number(N)),
    count(safe_flagged_neighbor(X,Y,_,_),F),
    count(safe_hidden_neighbor(X,Y,_,_),U),
    U > 0,
    N =:= F + U,
    safe_hidden_neighbor(X,Y,X2,Y2).

% Rule A_solo: Only one hidden and N=1
action(flag(X,Y)) :-
    cell(CX,CY,number(1)),
    findall((X1,Y1), safe_hidden_neighbor(CX,CY,X1,Y1), [(X,Y)]).

% Rule A2: CLP(FD) contradiction test
action(flag(X3,Y3)) :-
    cell(X3,Y3,hidden),
    component_with_hidden(Coords),
    build_model(Coords, Vars),
    post_sum_constraints(Coords, Vars),
    nth0(I, Coords, X3-Y3),
    nth0(I, Vars, Var),
    Var #= 0,
    \+ sat_component(Vars, 30).

% Rule B: All mines flagged → reveal rest
action(reveal(X2,Y2)) :-
    cell(X,Y,number(N)),
    count(safe_flagged_neighbor(X,Y,_,_),F),
    N =:= F,
    safe_hidden_neighbor(X,Y,X2,Y2).

% Rule C/Z: Reveal around 0
action(reveal(X2,Y2)) :-
    cell(X,Y,number(0)),
    safe_hidden_neighbor(X,Y,X2,Y2).


sat_component(Vars, Ms) :-
    Secs is Ms / 1000.0,
    catch(
        call_with_time_limit(Secs, once(labeling([ff,bisect], Vars))),
        time_limit_exceeded,
        fail
    ).

component_with_hidden(Coords) :-
    cell(X0,Y0,hidden),
    bfs([(X0,Y0)], [], Coords0),
    sort(Coords0, Coords), !.

bfs([], _, []).
bfs([(X,Y)|Q], Seen, Comp) :-
    memberchk((X,Y), Seen), !,
    bfs(Q, Seen, Comp).
bfs([(X,Y)|Q], Seen, [(X,Y)|Comp]) :-
    findall((NX,NY),
        ( neighbor(X,Y,NX,NY), cell(NX,NY,hidden) ),
        Ns),
    append(Q, Ns, Q2),
    bfs(Q2, [(X,Y)|Seen], Comp).

build_model(Coords, Vars) :-
    length(Coords, L),
    length(Vars,  L),
    Vars ins 0..1.

post_sum_constraints(Coords, Vars) :-
    forall(
        ( cell(CX,CY,number(N)),
          count(safe_flagged_neighbor(CX,CY,_,_),F),
          R is N - F, R >= 0,
          findall(V,
              ( neighbor(CX,CY,NX,NY),
                cell(NX,NY,hidden),
                nth0(I,Coords,(NX,NY)),
                nth0(I,Vars,V)
              ),
              Vs),
          Vs \= [],
          sum(Vs, #=, R)
        ), true).

next_action(A) :- action(A), !.
next_action(no_move).
