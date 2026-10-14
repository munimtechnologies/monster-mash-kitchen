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
  find it every day to grow a streak.

Made for RUN's October Jam ("Monster Mash"). Made by MV2 of Munim, Inc. with AI agents (Anthropic
Claude): the code, art and sound are all AI-made, and there are no premade assets. The art is drawn in
code and the sound is synthesized in the browser. Progress is saved in the browser only.

## Play and check

- Open `index.html` in a browser. Portrait, 720 x 1280, letterboxed on wider screens.
- Controls: tap or click. Keys: 1-9 and 0 pick ingredients, Enter or Space mashes and serves the next
  customer, Backspace takes the last ingredient back, B opens the book, S the shop, M turns sound on or off.
- `index.html#selftest` plays three nights and every screen through the real code and lists any problems.
- `index.html#demo` serves customers by itself (for videos); it never saves.
- `index.html#cover` draws the covers (1024 x 1024, 720 x 1280, 1280 x 720).

## Tests

    python -m unittest -v test_monster_mash.py

Static checks always run. With Node.js installed, the rules block must pass its own checks (every order can
earn 3 stars with the first eight ingredients, 45 different monsters, the Moon Recipe and streak rules), and
the whole page runs against a stub browser: a night played with clicks, keys, the shop, the book, the Moon
Recipe and a phone-shaped window.

`capture.py` (Playwright) runs the self-test in headless Chromium and saves screenshots, covers and a
portrait demo video.

## Licence

Apache-2.0. Copyright 2026 Munim, Inc.
