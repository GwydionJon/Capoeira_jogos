# Jogos Manager
A precompiled exe can be found here: https://heibox.uni-heidelberg.de/d/bcc9bd5e5f134dde87a9/

An online version can be found here: http://gwydiond.pythonanywhere.com/

Note that the online version has only a limited amount of cpu power, thus I recommend running the program locally.
You are free to compile the program yourself, further infos blow.


This program was designed for my capoeira group `Mare Alta` for use in our tournament.
Its job is to simplify the point calculation as well as the determination of the next round.

To use this program you will need an excel file similar to the provided [example](https://github.com/GwydionJon/Capoeira_jogos/blob/main/examples/example_excel_file.xlsx) in this repository.
You can add as many categories and people as you want.
The groups in each category are determined automatically at random based on a specified seed.
This ensures, that when the program is closed and reopened the same input file will result in the same chave arrangements.


### How to use:

#### The excel file:
In the provided example you can see two pages one named `cat A` and `cat B`, these are used for separating the tournament in different categories, which for examples can be based on specific cord colors.
In each category are a few columns though only `Apelido` and `Name` are absolutely mandatory and need to be spelled **exactly** like in the example. The rest can be freely edited, removed, extended or added.
If no `apelido` is given for a person their `Name` will be copied into the `Apelido` column instead.
The program will attempt  to build chaves with 4 participants in them, when the last chave can not be filled completely `platzhalter` will be added. Any points assigned to these are ignored.


#### Using the manager:
Note: currently all Game Points are multiplied by 0.9. This ensures sufficient importance of the game points while also reducing the likelihood of multiple people having the same amount of points.

After selecting a suitable excel file you are presented with multiple tabs that represent your different categories.
These should correspond to the different page names in the excel file. Under the tab is a sortable list of all participants and their overall points.

Under the table you will find another tab for each started round.
These are typically the preliminary, quarter- and half-final and the final.
For each shave in a round you can find a table with the different game combinations.

In each round you can find a list of the current points for this round, while the total points are presented in the table above.

The different colors in each chave represent possible different game types. For example red are the Sao bento games, yellow Benguela, green and purple Iúna or Angola respectively.
This should when for example first all rounds of Sao bento are played in all shaves before starting with Benguela. If the given game type is not present in a category just leave the fields empty or just use them for another game type.

When multiple shaves are present you can use the color to coordinate the different game types. For example first all Sao bento games are played in all shaves and their points entered in the red fields.

Hint: you can add multiple numbers with the `+` sign like: `3+4+5` into a field. This will than be summed up automatically.

Finally after all games have been played you can start a new round by first selecting the number of players to advance at the bottom of the page. When the `start new round` button is pressed you will be asked to confirm the players. Currently the program does not automatically handle a scenario where two players have the same number of points. It will simply pick one of them over the other. This means you have to make sure this is not the case and decide the winner by adding him some small amount of points in one of his games.

#### Saving and backup:
When run locally the program will create a backup excel file after each. In the case of a crash or power loss simply restart the program, load the same excel file and use the `jogos_result` file to reconstruct the points.
Note that this is not available when running the hosted version.

#### Compiling to exe:
If you don`t want to use the provided executable you can simply compile it yourself after checking the source code.
You will need a working [python installation](https://www.anaconda.com/products/distribution) for this.
simply clone the repository, pip install `pyinstaller`
and run the provided `build_exe-sh` script.



If you encounter any problems please open an issue at https://github.com/GwydionJon/Capoeira_jogos/issues.

Future plans:
- Handle multiple participants with identical points.
- Provide a comprehensive result table at the end of a tournament.
- Provide portuguese language support.
- Add option to directly load the jogos_result file as a backup.