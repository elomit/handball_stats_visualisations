This is horrible programming, but it is just a start!

# Review:
## Abstrakt:
 - noch mehr aufspalten in methoden
 - bei der masse an code auch aufspalten in mehrere files
 - mehr funktionale Architektur, aufpassen mit global states
## Kleinkram:
 - files immer auch schließen (also .read() und danach .close())
 - tendenziell eher positive checks machen (also statt != "Fehler" lieber == "Tor" oder isin(["Tor", "Gehalten"]))
 - wenn nur zwei Datenpunkte möglich sind (Handballfreunde oder Gegner) lohnt es sich bei bools zu bleiben - wenn man die dann noch passend nennt (also zb. "is_own_team" statt nur "own_team"...) bleibt der code kürzer und lesbarer
 - du hattest die Dateinamen für die Shots ohne Location erstellt, die haben sich die ganze Zeit überschrieben