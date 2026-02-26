# Poptracker
Guide written by STQ, updated for Gregipelago by Gregorovich

## Installing Poptracker & Packs

Download Poptracker zip from the github ['latest releases'] (https://github.com/black-sliver/PopTracker/releases/latest) page. You will likely need the win64 version, but choose the version from the "Assets" list suitable for your operating system.

### On Windows:

* Extract the win64.zip file contents to wherever
* Download the tracker pack zip file for your game
* Place the zip in the Packs filepath
    * DO NOT EXTRACT THE GAME PACK ZIP
    * The below screenshot is to help you find your filepath:

![Poptracker Filepath](https://media.discordapp.net/attachments/1339189542732955749/1472688605322416248/image.png?ex=69a15364&is=69a001e4&hm=34181ccf44e2193e4b03c685280d18430b2d0aa524db99cd4d59b9776e5954f5&=&format=webp&quality=lossless "Poptracker Filepath")


## Setting-Up Poptracker

You can now open up Poptracker and click the folder icon in the top left then choose the game and subsequent tracker type you want (recommend the map one if there's more than one option). Poptracker will also automatically open your last used game tracker.

![Opening a Poptracker Pack](https://media.discordapp.net/attachments/1339189542732955749/1472688605955887174/image.png?ex=69a15364&is=69a001e4&hm=46be8aca273a53eb04a21308bf6258cebdb6fd35c4253ce8981df4d61fc1fc62&=&format=webp&quality=lossless "Opening a Poptracker Pack")

Once your pack is open, you normally get an overworld map, and options for more local maps (if supported).

### Connect to your AP slot to sync it with our AP session

Click the "AP" icon in the top of the application
* In the first pop-up box, enter the server address and port number (e.g. gregipelago.co.uk:42069) and submit
* In the second pop-up box, enter your slot name and submit
    * This is case sensitive, so check your tracker / Discord information page if you are unsure
* In the third pop-up box, enter the session password, or leave blank if not application, and submit
    * Note: Poptracker may not tell you if it fails to connect (e.g. wrong slot name, wrong password, wrong pack for slot game)

The AP icon should turn green to show it is connected, and hopefully your tracker will have at least some boxes change colour

## Using Poptracker

There is not an enforced standard for how a Poptracker pack must be presented, therefore this guidance is generic and may differ slightly to your specific pack.

You may have Region selectors across the top of your pack, and under each region, a Sub-Region selector. Some packs may use these as literal regions within your game, others may use it as gameplay areas / options (Story mode vs Mission Mode). You can navigate through these to find specific checks as necessary.

![High Level Region Map](https://media.discordapp.net/attachments/1339189542732955749/1472688606442160170/image.png?ex=69a15365&is=69a001e5&hm=c59091fe8174a176bf0f8de3e559a5d0084dbeec3d880ed1f1eb34466a514e01&=&format=webp&quality=lossless "High Level Region Map")

![Sub-Level Region Map](https://media.discordapp.net/attachments/1339189542732955749/1472688607016783883/image.png?ex=69a15365&is=69a001e5&hm=cb4e1a7904728abc13b8d79f84801124fb36323ac209e4a598584dff0b57c377&=&format=webp&quality=lossless "Sub-Level Region Map")

A coloured square on your tracker will denote a Location, which could be a single check, or a group of checks (shown by hovering over the square). The colour of the box will denote different things (multiple colours can be present). If you hover over a square, you may get a single check or multiple. Each of the check names will have a title that changes colour (in line with the colour descriptions below) and usually an icon that changes depending on whether you have collected that check according to the AP server. The colours are as follows:

- Green: A check here is within logic and you should be able to collect it
- Yellow: A check here is outside of logic, but is potentially possible to collect with glitches
- Red: A check here is not possible in or out of logic, you should not be able to collect it
- Grey: A check here has been collected already

A box on your tracker will only turn grey when all checks are completed, you will not get partially grey boxes. The title of the check, however, will turn grey when you collect it.

Note: You may need to click the cog looking option to add any specific randomiser options you have in your YAML (not applicable for all games), and change any other settings you might want for your tracker (e.g. do not spoil entrance randomisers)