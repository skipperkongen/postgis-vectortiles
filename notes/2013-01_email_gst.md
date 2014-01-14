# Email to Anders Friis-Christensen

Date: January 2013

```
Hej Anders

Her er et par ord angående vector tiles, som er et emne jeg kunne tale om for DOS/LIF

Vector tiles
En vector tile har meget til fælles med en raster tile
- Et geografisk dataset kan deles op i en mængde af tile grids, et grid for hver skala. Et grid indeholder tiles.
- En tile indeholder geografisk data indenfor en rektangulær (ofte kvadratisk) bounding box
- Data er tilpasset til skala. Det kan være generalisering/simplificering af linjeforløb samt filtrering af data (ift en kartografi).
Forskellen er at en vector tile indeholder vector data i stedet for raster data. 

Det primære formål med en vector tile er en form at distribuere geografiske data på. Der er to nuanceringer af dette.
1) Man kan bruge vector tiles til at rendere forskellige raster tiles mere effektivt. Der spekuleres på gis.stackexchange.com at Google renderer raster tiles on-the-fly da der tilbydes bruger-definerede map styles. En effektiv måde at generere mange forskellige raster tiles på er, at gemme vector tiles og style disse til forskellige raster tiles. (Google tilbyder nu bruger-definerede map styles)
2) Man kan sende vector tiles direkte ud i klienten, som så renderer dem med f.eks. HTML5 (hvis klienten er en browser). Fra browserens synspunkt hentes vector tiles stort set som raster tiles, med lidt ekstra bogholderi med at merge vector data fra tiles ind i et vector lag.

Udfordringer og trade-offs: Hvis man vælger at "klippe" features over når de breder sig ud over flere tiles, er der nogle geometriske egenskaber som areal der går tabt. Hvis man vælger at gemme en hel feature i en vector tile, hvis feature intersekter tilens bounding box får man gemt (og klienten risikerer at hente) den fulde feature mange gange.

Målsætningen er at klienten kun skal hente data nogenlunde svarende til det antal geometri vertices som kortets udsnitsvindue p.t. intersecter. Et eksempel er Danmarks kystlinje. Benytter man vector tiles i klienten og brugeren zoomer ind på Køge, ville det være hensigtsmæssigt at klienten ikke downloader hele Danmarks kystlinje, men kun det udsnit der ligger tæt på Køge. Det peger på at en model hvor man gemmer:
1) Features croppet til vector tile bounds (en feature kan således være delvist gemt i flere vector tiles). Tabte geometriske egenskaber som areal gemmes i en attribut. Features kan bindes sammen på feature-ID på tværs af vector tiles, så den originale feature kan genskabes i klienten
2) En model hvor man eksploderer en feature geometri til dens vertices, som så bindes sammen til feature-id (lidt vagt på nuværende tidspunkt)

Vælger man en model hvor hele Danmarks kystlinje hentes når man ser på Køge, men kun en gang per klient session:
1) En model hvor man gemmer en liste af feature-id i vector tile (id for de features der er indeholdt i tile), og selve feature så hentes med sekundære web service kald (såfremt klienten ikke allerede har hentet den). Her ville det være hensigtsmæssigt at klienten kun foretager et enkelt eller få web service kald, som så batcher feature-ids (som klienten ikke kender i forvejen) sammen.
2) Et tillæg til denne model er at klienten kan hente geometri i forhold til det nuværende zoom-forhold, så der modtages en simplificeret udgave af geometrien

Der er mange muligheder, og derfor rig mulighed for at DOS/LIF giver feedback på et tidligt tidspunkt i processen.
```