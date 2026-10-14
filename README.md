# Monster Mash Kitchen

A cozy-spooky cooking game for phones, in one HTML file. You run a midnight kitchen where monsters are
made by mashing two ingredients in a bubbling cauldron.

- **Mash:** tap two ingredient cards, then MASH. Every pair of different ingredients makes its own monster,
  always the same one: 45 to find, each with a name, a one-line bio and a look built from its two ingredients.
- **Serve:** costumed villagers order by stats ("cute but gooey", "the spookiest thing you have", "surprise
  me!"). A monster's Spooky, Cute and Gooey (1 to 5) are 1 plus what its two ingredients add, and each
  card shows what it adds. Up to 3 stars per order, six orders a night.
- **Collect:** the Monster Book shows what you've found and silhouettes for the rest. Coins buy two more
  ingredients (17 more monsters) and new cauldrons.
- **Moon Recipe:** one secret pair a day makes a glowing moonlit monster. The clue gives away half of it;
  find it every day to grow a streak, and each day of the streak pays 10 more coins (up to +70).

Made for RUN's October Jam ("Monster Mash"). Made by MV2 of Munim, Inc. with AI agents (Anthropic
Claude): the code, art and sound are all AI-made, and there are no premade assets. The art is drawn in
code and the sound is synthesized in the browser.

## On RUN

RUN's game frame has no `localStorage`, so the RUN build loads RUN's SDK before the game
(`window.RundotGameAPI`). When it is there, the game:

- saves the kitchen to the player's RUN storage (`appStorage`), and waits up to 4 seconds for it on start;
- adds a **Share** button to each monster card: the link carries that monster, and a friend who opens it
  gets a hint line and +25 coins for mashing the same one;
- offers an **optional rewarded ad** at the end of a night that doubles that night's coins, once a night,
  only when RUN says an ad is ready;
- after the day's Moon Recipe is found, schedules a **local reminder** for 6 pm the next day.

Every SDK call is wrapped so that a failure can't stop the game. Anywhere else (a plain browser, itch.io)
none of this appears and progress is saved in the browser.

`build_run.mjs` makes the RUN build: `npm install`, then `node build_run.mjs run-dist` writes
`run-dist/dist` (deploy that folder with `rundot deploy`) and `run-dist/build-report.json`. RUN's SDK
(`@series-inc/rundot-game-sdk`) is not part of this repository and keeps its own licence.

## Play and check

- Open `index.html` in a browser. Portrait, 720 x 1280, letterboxed on wider screens.
- Controls: tap or click. Keys: 1-9 and 0 pick ingredients, Enter or Space mashes and serves the next
  customer, Backspace takes the last ingredient back, B opens the book, S the shop, M turns sound on or off.
- `index.html#selftest` plays three nights and every screen through the real code and lists any problems.
- `index.html#demo` serves customers by itself (for videos); it never saves.
- `index.html#cover` draws the covers (1024 x 1024, 720 x 1280, 1280 x 720).

## Tests

    python -m unittest -v test_monster_mash.py

Static checks always run, including that every RUN SDK call goes through the guard. With Node.js installed,
the rules block must pass its own checks (every order can earn 3 stars with the first eight ingredients, 45
different monsters whose share keys lead back to them, the Moon Recipe, streak and bonus rules), and the
whole page runs against a stub browser: a night played with clicks, keys, the shop, the book, the Moon Recipe
and a phone-shaped window, and a session on RUN with a fake SDK (the saved kitchen loads, a friend's link
pays its bonus, Share, the rewarded ad and the reminder).

`capture.py` (Playwright) runs the self-test in headless Chromium and saves screenshots, covers and a
portrait demo video.

## Changes

- **0.2.0:** RUN support (player storage, share links with a friend bonus, an optional rewarded ad, a daily
  reminder), a streak bonus for the Moon Recipe, and the result card re-laid so the "Perfect night" line is
  no longer hidden under the button.
- **0.1.0:** first version.

## Licence

Apache-2.0. Copyright 2026 Munim, Inc.
