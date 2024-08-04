# tictactoe
Trying out DeepMind reinforcement learning / neural net concepts

Before doing evaluation & learning process, define which player I am: WhoAmI

That allows reward function to be reduced from this crazy vector thing I have now
to a simple scalar value, which is the way it should work.
State must include which player I am in order for values to reduce.

Could I simply define which player I am to be whoever is next to play?
I think so.  Try this approach.

In context of tic tac toe, we're trying to work out an optimal policy both for X, and for O.
They are separate policies.  Their combination yields a single, unified policy, which in the end is what we're after.
But policy for X has rewards and values computed from X's point of view, and likewise for O.
Don't try to do both at the same time.

In zero-sum games such as we're looking at now, my value is simply the inverse of my opponent's value.
But of course not all games work this way.

--------------------------------------------------------------------------------------
Example

Take state S0 as:
     X | O | -
     ---------
     X | X | O
     ---------
     - | O | -

Say we are looking at this state for the first time, and have no prior information on this
or any other state in the game.

From game rules, we know:
    1. Last to play was O                   Method: last_to_play
    2. The game is not over, so reward to this state (for O) is zero
        R(S0) = 0                           Method: reward
                                            Note: reward is always from perspective of last_to_play (O here),
                                            so if O had played last and won here, reward would be 1
    3. X is to play
        N(S0) = X                           Method: next_to_play
    4. Three actions are possible
        A(S0) = (2, 6, 8)                   Method: actions
    5. And will result in three future states
        S(A) = (Sa, Sb, Sc)                 Method: states

Never having visited S0, its value and policy will be gotten (initialized) as:
    Value initialized to reward: 
        V(S0) = [R(S0) =] 0                 Method: value
                                            Note: value is always from perspective of next_to_play (X here)
    Policy initialized as uniform random choice: 
        P(S0) = (1/3, 1/3, 1/3)             Method: policy

Now, conduct a one-step revision.
    Get Sa, Sb, Sc values
    Use Sa, Sb, Sc values to revise S0 policy
    Use Sa, Sb, Sc values and revised S0 policy to revise S0 value

We have never evaluated Sa, Sb or Sc.  So their values must be initialized, as above:
    V(Sa) = R(Sa) = 0           Game still not over
    V(Sb) = R(Sb) = 1           X, last to play in this state, wins
    V(Sc) = R(Sc) = 1           X, last to play in this state, wins

When we "get" the values for Sa, Sb and Sc, we don't calculate or revise:  
    we simply ask what their (pre-computed or initialized) values are at the moment (time t)
To revise S0 policy (from time t to new time t+1), 
    we use a greedy policy against the values for Sa/Sb/Sc, which are 0/1/1, 
    adjusted for some random factor to allow for exploration.  
    So maybe 0/0.5/0.5 becomes 0.1/0.45/0.45
Then, to revise the value of S0, 
    we apply revised policy (0.1/0.45/0.45)
    to retrieved values for Sa/Sb/Sc (0/1/1)
    So value revises to 0.9
        
With calculations and revisions complete, we move on to actual state transition and learning.
We choose a next state from Sa, Sb, Sc, based on our revised policy.
    If we choose either Sb or Sc, we reach a terminal state.
        Terminal states have no value or policy revision; they're unchanging, so we're done.
    
--------------------------------------------------------------------------------------
If we choose Sa, however, we have to iterate again:
    
State Sa:
     X | O | X
     ---------
     X | X | O
     ---------
     - | O | -

Now we know:
    Last to play was X
    Game is not over so reward for X is zero
    O is next to play
    2 actions are possible:  (6, 8)
    Call the future states (Sd, Se)

Sa value was initialized in previous iteration to 0.
    V(Sa) = [R(Sa) =] 0
Initialize Sa policy as uniform random choice:
    P(Sa) = (0.5, 0.5)

Getting (initializing) Sd, Se values:
    V(Sd) = 0               Game still not over
    V(Se) = 0               Game still not over

Revising Sa policy:
    A greedy policy against Sd/Se of 0/0 will be 0.5/0.5
    So revised policy computes to same as old policy:  0.5/0.5
Revised Sa value
    Retrieved values (0, 0) against revised policy (0.5, 0.5)
    Still yields value of 0
    
And again, with calculations and revisions complete, we move on to actual state transition and learning.
We choose a next state from Sd, Se, based on revised policy.
    If we choose either Sd or Se, we will still not be done; the game won't be over.


--------------------------------------------------------------------------------------
So at random let's choose Sd and proceed.

State Sd:
     X | O | X
     ---------
     X | X | O
     ---------
     O | O | -

Now we know:
    Last to play was O
    Game is not over so reward for O is zero
    X is next to play
    1 action is possible:  (8)
    Call the future state (Sf)

Sd value was initialized in previous iteration to 0.
    V(Sd) = [R(Sd) =] 0
Initialize Sd policy as uniform random choice:
    P(Sd) = (1.0)

Getting (initializing) Sf value:
    V(Sf) = 1               Game over, X wins

Revising Sd policy:
    A greedy policy against Sf of 1 will be 1.0
    So revised policy computes to same as old policy:  1.0
Revised Sd value
    Retrieved value (1) against revised policy (1.0)
    Yields value of 1

We reached a terminal state so our learning for this path is done.
Note, however, that the value of state Sd, which was initialized to 0 (since game isn't over in that state),
was revised to 1 (for X).  The next time we visit state Sa, we will use the new value of Sd to revise the Sa
state downward (since in Sa, O is to move, so Sd value for O is -1, the opposite of X's value there).
The negative value for O in these states will propagate backward, trial by trial, until the action that led
to our starting state of Sa will be valued by O as negative, and O will choose some other action-- presumably
to block X instead.  And this is the learning we want.

