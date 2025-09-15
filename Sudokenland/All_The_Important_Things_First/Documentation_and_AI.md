# Sudokenland — Development and AI use

**Start**

When I first started thinking about the project and what I wanted to do, I knew that I wanted to create something related 
to the game Sudoku, which I like to play. It seems to be a game that is easily programmed, since it is based on pure logic 
with numbers that always have to be arranged in the same way. But then, I realized how difficult it would be to create everything
in one code, which is why I tried to seperate big and complex functions from the main game content, as I had described in the 
presentation video. This process took me way longer than I expected and I had to make many modifications to my original plan.
I used AI to help me to bring some ideas that I had to life, since the complexity of many functions that I needed was too
high for me as a Beginner to come up with all by myself. In the following Development log I tried to mark and explain 
the functions and files that I used and how AI helped me with some.

I wrote this vlog stepp by step to explain my intent, the functions I created, why I needed them, and what went wrong along the way.

AI assistance disclosure: Parts of the design and some code snippets were co-authored with an AI assistant by OpenAI. 
I firstly tried to code as mcuh of the basic code and its core functions, but especially when it came to connecting everything 
in a structured way I needed assistance. I reviewed, adapted, and tested all code before committing it.
I profited from the tips and even additional functions that AI suggested and learned even more about how to structure my coding.

I hereby certify that I have written this thesis (in the case of a group thesis, your part of the thesis should be marked accordingly) independently and have not used any sources or aids other than those specified.
I have correctly cited all passages that I have quoted or paraphrased. I have not yet submitted the thesis in the same or a similar form for any other course or examination authority.

**ascii_assets.py**

I began with visuals because I wanted story screens to feel alive without pulling in a full image pipeline. I did so by creating ASCII portraits. 
In `ascii_assets.py` I created a file that holds four entries: `queen`, `dyskalkulo`, `howard`, and `howardice`. 
Each entry is a list of text lines that forms a portrait when rendered in a monospace font.
I added a helper `render_ascii_surface(ascii_lines, size=16, fg=(255, 255, 255), bg=None)`. 
This function loads a monospace font, measures the widest line, calculates the pixel width and height from the font metrics,
allocates a Pygame surface, and then blits each character at the correct x and y. It returns a surface with an alpha channel 
so backgrounds can remain transparent. I built it this way to keep all art and its rendering in one place. The first struggle 
was caption spacing. I wanted names under portraits without misalignment, so I added internal padding inside the rendered surface and kept a 
consistent baseline so captions sit nicely under different portraits.

**AI USE** I was struggling with the adjustement of size and its placement and after I had done the ASCII code, so I asked ChatGPT to help me with 
the formating. Thus, the rendering came alive and the function forcing it ('render_ascii_surface).

**Sudokenland.game.py**

With the portraits available I focused on the global flow and the file where I wanted to make everything come together.
I created `Sudokenland.game.py` and wrote the main state machine and the first three screens. 
The state loop lives inside `main()` which creates the window, sets up a clock, and switches on a `state` string. 
Each screen function returns a next state string and optional payloads. I also defined `BASE_DIR`, `ASSETS_DIR`, `DATA_DIR`, and `FONTS_DIR` at the top so file. 
Input and Output is always relative to the project root.
I implemented `screen_title(screen, clock)`, `screen_character_select(screen, clock)`, and `screen_story(screen, clock, selected_name)`. 
Title listens for ENTER to advance and ESC to quit. Character select uses the ASCII renderer from before and saves the choice with `save_selected_character(name)` so I can greet the player by name later.
Story draws the Queen and Dyskalkulo portraits and asks for help;
pressing Y advances, N shows a short blackout message and returns to title. I wrote two small helpers, `load_font(size)` and `draw_centered_text(surface, text, y, font, color)`,
so type and layout look consistent across screens. I made each screen a pure function that polls events, draws, and returns a result because this keeps transitions explicit and debuggable.


**AI USEE**
Creating this interactive/ input-output code really made me struggle with the overall feedback and how to implement it into the following
code. I used AI to help me bring a structure to my code and where to put which loop and function so that it would make sense.

 **create_levels.py generator**

I needed actual puzzles and I was honestly too lazy to just copy some already made from the internet, so i created a function,
that created the Sudoku for me. However, it was harder than I expected due to the mathematical or logical rules that I had to implement.

find_empty(grid) -> Optional[(r, c)]
is_valid(grid, r, c, val) -> bool
solve_grid(grid) -> Optional[solved_grid]
count_solutions(grid, limit=2) -> int
generate_full_solution() -> solved_grid
make_puzzle(solution, clues_target, max_tries=10000) -> puzzle_grid
build_level(level_index, clues, seed=None) -> dict
main(force: bool)

`solve_grid` is a randomized depth-first backtracking solver. It shuffles candidate numbers to avoid reproducing the same board each time.
`count_solutions` uses the same search but stops when the counter reaches two. That early abort is enough to detect non-uniqueness and keeps the runtime under control. `generate_full_solution` seeds the three diagonal 3×3 boxes with shuffled values before calling the solver; this speeds up convergence because those boxes do not constrain each other. `make_puzzle` starts from a full solution, shuffles all cell coordinates, and removes numbers one by one. For each removal I call `count_solutions`; if it returns one, the removal stands, otherwise I revert it. I exposed a `LEVEL_CLUES` list so I can target more clues in early levels and fewer clues later. `build_level` packages `level`, `clues`, `grid`, and `solution` into a JSON-ready dictionary. In `main` I iterate levels 0 through 9, use a per-level seed for reproducibility, and write each file under `Assets/data`. My goal was to produce content that is solvable and uniquely solvable so the runtime never needs heavy validity logic.

 **verify_levels.py and missing data**

I wrote `verify_levels.py` to confirm every level JSON is correct before the game loads it. I reuse solver logic equivalent to `solve_grid` and `count_solutions`.
For each file I check shape, solve it, and assert that the solution count is exactly one. While running it I realized `level_8.json` was missing. To fix this quickly I extended the generator with a `--only N` flag and created `level_8.json` without touching other files. 
I also decided to show an explicit message on the world map when a level file is missing so the player is not left guessing.
**AI USE**
I realized during playing the game myself that the sudoku did not always make sense as they did not lead to a solution.
I asked ChatGPT what I could do to prevent this, which led me to the `verify.levels.py`. It helped me to create the solver logic function. Until today I still do not know why the `8.json`was missing...

  **sudoku.py layout, state, and drawing**

I switched to the gameplay screen and wrote `sudoku.py`. 
The entry point is `start_sudoku(level_index, data_dir) -> str`. It loads `Assets/data/level_{level_index}.json`, constructs state,
and runs a loop that returns `"completed"`, `"back"`, or `"quit"`. State holds `start_grid`, `solution`, `current_grid`, `fixed_mask` derived from the start grid so original clues cannot be overwritten, a selection `(row, col)`, and a transient status message.

For drawing I wrote `draw_board(surface, state)` to compute a dynamic cell size from available width and height, center the board, 
and draw thin lines and thicker lines at subgrid boundaries. My first attempt placed help text right over the grid which looked messy.
I moved help rendering into `draw_help_overlay(surface, state)` which paints a translucent strip along the top and writes the controls into it, so that
short messages appear through `draw_status(surface, message)` at the bottom. This layering keeps the grid readable and the controls visible at all times.

 **AI USE**

For this screen I consulted OpenAI to validate the API shape start_sudoku(level_index, data_dir) -> str and to settle on three explicit return states (completed, back, quit). 
 The assistant suggested separating drawing into draw_board, draw_help_overlay, and draw_status to avoid overlay conflicts,
 and recommended keeping a fixed_mask derived from the start grid so original clues cannot be overwritten. The alternating hint behavior and the key map (H for hint, L for auto-solve, E for back) were co-designed with ChatGPT. 
 I integrated these ideas, rewrote the code to fit my layout, and tested the interactions; mistakes were mine and were fixed during manual runs.



**sudoku.py input, hint system, and auto-solve**

I finished the interaction. The event loop routes input into small helpers. 
`move_selection(dx, dy)` clamps the cursor between zero and eight. `write_digit(d)` writes to `current_grid` but consults `fixed_mask` first 
so fixed cells are never changed.
`clear_cell()` clears the current cell with the same rule. Hints live in `apply_hint(state)` and alternate behavior each time H is pressed.
On one press I reveal one correct digit by scanning for a cell that is empty or wrong and copying the value from `solution`. 
On the next press I produce a short text tip that points at a specific 3×3 box or a suspicious row and column; I keep a toggle flag in state for this alternation. 
Auto-solve is implemented in `auto_solve(state)` which copies non-fixed values from `solution` into `current_grid`, sets a message, 
and causes the loop to return `"completed"`. Completion detection is a straight equality check `current_grid == solution` 
that runs after each edit and at frame start so manual solves and auto-solve share the same success path. Controls are arrows and WASD to move, 1 through 9 to write, 
0 or BACKSPACE or DELETE to clear, H for hint, L for auto-solve, E to go back to the map, and ESC to quit. 
My main struggle here was avoiding accidental edits to fixed cells;
the explicit `fixed_mask` solved it cleanly because every mutating function consults it.


**world map and persistent progress in Sudokenland.game.py**

I returned to `Sudokenland.game.py` to build the world map and progression. I added `save_progress(unlocked_until)` and `load_progress()` 
which read and write `Assets/data/progress.json` with a single integer field named `unlocked_until`.
I wrote `available_level_files()` to scan `Assets/data` for `level_X.json` files so I can draw nodes and detect missing files. 
The screen function is `screen_world_map(screen, clock, unlocked_until)`. It draws ten circular nodes labeled zero to nine.
The selection index is clamped so I cannot move into locked nodes. When ENTER is pressed I check whether the target file exists and whether it is unlocked. 
If a file is missing I show a short message. If it is locked I tell the player which level must be solved first. If it is valid I return `"run_level"` with the index.
Then I continued to do `run_sudoku_level(level_index) -> str` which imports `start_sudoku` locally to avoid circular imports and returns its result. 
I also made sure that whenever the program transitions into the world state, the main loop reloads progress from disk and passes that value to `screen_world_map`. 
That detail matters for the reset flow later.

**AI USE**
I consulted AI (Notion) on when to reload progress from disk to make resets take effect immediately. 
The load-on-entry approach for the world map and the explicit messages for missing or locked levels came from that review; I integrated and tested the changes.


 **level-done, queen lines, and ending**

I added `screen_level_done(screen, clock, level_index)` for levels zero through eight. It shows “Level N done” and a line from the Queen.
I wrote `get_queen_message(level_index)` which returns exact level-specific lines. Zero says that the first digit returns to the realm, one says order grows stronger,
two says twogether we can do this and Dyskalkulo trembles, three says threelling, four says FourEver four the numbers, five says give me five, six says sixy save,
seven says almost there and even Dyskalkulo must admire the solve, eight says greight job.

Well, I initially wired the ending to fire after every level. That was wrong because it killed pacing and interfered with the actual workflow/gameflow.
I fixed it by gating the ending strictly 
on `level_index == 9` in the main loop so only the ninth level transitions into the finale. 
That change made the loop feel natural again.

I also implemented a reset flow. `reset_all_progress()` deletes the progress and selected character files and writes `{"unlocked_until": 0}` back to disk.
`confirm_prompt(screen, clock, question)` shows a simple yes or no prompt so resets are intentional. I bound this to the R key on the title screen and on the map.

**free-play bug and map clamping**

After adding reset I noticed that the world map still behaved like free play even when I had just reset progress. The bug was that I read 
progress once at startup and kept it in memory. The fix was small but important. In the `main()` loop I reload progress from disk right when switching 
into the world state and pass it into `screen_world_map`. From that point on the selection clamp reflects the latest saved state and a reset takes effect immediately.

 **ending and epilogue**

I refined `screen_ending(screen, clock)`. It first displays a short fireworks visualization with a thank-you line from the Queen, 
then cuts to a two-line epilogue. The epilogue reads: You feel happy, but dizzy suddenly. The world starts turning in front of your eyes and you faint.
After a short display time the function returns `title` which brings the game back to the opening screen. 
I kept the ending on a timer rather than a keypress to avoid accidental skips and to keep the pacing consistent.

**AI USE** 
I did not know how to finish and exit the game altogether in a way that it would come back to my home screen, so I turned to AI.
Also, it helped me with creating the fireworks.

**Comitting**
I comitted the whole project altogether, because I made so so many changes over the span of two weeks where I deeply worked on the 
project. Thus, I decided to keep order by doing this documentation log so that one can understand my way of working and approach to 
different problems and the structure.