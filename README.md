Ableton Live Control Surface for Teenage Engineering OP-1 

Copyright (C) 2012 Imaginando, Lda & Teenage Engineering AB
   
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For more information about this license please consult the
following webpage: http://www.gnu.org/licenses/gpl-2.0.html

===

LAST UPDATE - 28 Jul 2017
- code cleanup
- docs

16 May 2017
- fixed bug that prevented clear button (ss8/m2) from working properly on sessions with track groups

15 May 2017
- shift + paste (arrow down) button is undo now
- shift + scissors is redo

14 May 2017
- shift + seq button will toggle "follow song" option
- improved text of a scene or a track displayed on OP1 - unprintable chars are removed, spaces joined together and string is limited to 20 chars (OP1 display limit)
- encoder 4 in transport mode will control size of a track widget on press + turn

27 April 2017
- fixed assert raising bug appearing when script was accessing non-existing slot (related probably to groups)

26 April 2017
- mic and com button select track in transport mode
- better toggle of views
- pressing rec buton while recording will only stop record state, not the playback

22 April 2017
- OP1 can now control transport params of Ableton in "transport mode" (tape)
- shift + arrows jumps to next/previous marker
- lift button sets/unsets a marker
- shift+lift hides/shows the browser
- blue encoder scrubs the tape (even while playing)
- green encoder changes quantization parameters
- white encoder moves the play position and makes a selection while pressed
- orange encoder zooms arrangement view when in transport mode
- shift + play plays a selection (if there is one)
- shift + loop in sets the beggining of the loop to the current play position
- screen now displays play state, quantization and BPM

8 September 2014

- The main problems with the Live 9 version of the scripts were fixed.
- The red box appears again and the song position arrows work again but with a workaround as I still couldn't understand why set_seek_buttons of the TransportComponent aren't working.

INSTALLATION

- Please note that folders in the "MIDI Remote Scripts" folder must not contain dashes. Otherwise python will fail to import the module.

- Mac OSX

 Right click on Live App bundle and click "Show Package Contents"
 Navigate to "Contents\App-Resources\MIDI Remote Scripts"
 Drop OP-1 folder into MIDI Remote Scripts Folder

- Windows

 Look for Ableton Live executable file
 Look for the folder MIDI Remote Scripts
 Drop OP-1 folder into MIDI Remote Scripts Folder

- Finalize

 Go to Ableton Live MIDI preferences
 Choose OP1 Control Surface

- For operation details give a look on TE-OP1-Mapping-Guide.pdf

==

Developer: Nuno Santos (Imaginando, Lda)

For related questions please use the contact form at www.imaginando.pt
