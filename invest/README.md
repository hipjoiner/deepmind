# invest
Trying out DeepMind reinforcement learning / neural net concepts

Tic Tac Toe is basic but working.

This will be a try at an investment game.

Players are different:
    Player 1 is me, the investor, deciding to buy and sell.
    Player 2 is Mr. Market, deciding how to alter prices.

So there will be no winner or loser, only my final score at the end of the game, which I seek to maximize.

Process:
    Turns will go one per day.  Each day:
    I'll have company information from financials
    I'll have a price at which I can trade
    My turn will consist of a decision to buy, sell, or do nothing.
        Start with a cash stake, say USD 10,000.
        If I buy, it will be with all the cash I have
        If I don't buy, the amount remains in cash (maybe earn cash return later)
        If I sell, I sell everything, converting back to cash
    I make my move, the Mr. Market makes his move
        Mr. Market adjusts the market price for the asset.
    My learning will consist of assessing relative value of the asset, based on company fundamentals, and on market price.
    At outset, I'll have no historic price knowledge, only company financials.
    I'll need to seed with baseline values at start: e.g., P/E of 10 or less is buyable, etc.

Questions:
    Value should be total return over the time horizon.  What time horizon?
        Start by backtesting all available data days.  Use the entire time span.
    Should I assume transaction costs? 0.1%?
    How to construct policy pdf?
        Uniform PDF is straightforward: 
            If flat, either stand or buy. 
            If long, either stand or sell.
            Equal weighting either option.
        Greedy PDF: what does it look like?
            Same as in tic-tac-toe: always choose option that shows highest value estimated so far.
        Starting explore factor could be important

Required properties/methods for state:
    choose_play -- based on policy, and next_play_states
    game_over
    next_play_states -- construct state of next day after potential plays have been made
    next_state_value
    next_plays -- for this starting game, easily determined
    policy_pdf -- easily set, but must be revised
    revise_policy_pdf
    revise_value -- based on next_state_value
    rewards -- market value at end of game??
next_play_states is harder for this game because state is really a distribution (price change), 
rather than a set of discrete scenarios. Or rather, next state can vary continuously with new price,
and I must assume/construct what I *think* is an appropriate pdf for the price change.
What properties defined state? The "board" must be things like 
    current P/E 
    1-year earnings growth
    etc.