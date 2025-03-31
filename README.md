This is horrible programming, but it is just a start!

# Review:
## Abstrakt:
 - noch mehr aufspalten in methoden
 - bei der masse an code auch aufspalten in mehrere files
 - mehr funktionale Architektur, aufpassen mit global states
 - rein fachlich finde ich die Timelines als Darstellungsform nicht passend gewählt, da müsste man (meiner meinung nach) sich was anderes überlegen 
## Kleinkram:
 - files immer auch schließen (also .read() und danach .close())
 - tendenziell eher positive checks machen (also statt != "Fehler" lieber == "Tor" oder isin(["Tor", "Gehalten"]))
 - wenn nur zwei Datenpunkte möglich sind (Handballfreunde oder Gegner) lohnt es sich bei bools zu bleiben - wenn man die dann noch passend nennt (also zb. "is_own_team" statt nur "own_team"...) bleibt der code kürzer und lesbarer
 - du hattest die Dateinamen für die Shots ohne Location erstellt, die haben sich die ganze Zeit überschrieben
 - Konstanten schreibt man meistens in CAPS_LOCK, damit man das besser erkennt (ist in python nicht ganz so relevant, da Konstanten hier nicht wirklich existieren)
 - wenn variablen unabhängig von eine loop sind, außerhalb erstellen (sonst macht der das jedes mal neu) -> bsp. full_game_analysis() die "treffer_list"