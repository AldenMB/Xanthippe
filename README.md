# Xanthippe

![an animated GIF of the Xanthippe circuit running](xanthippe.gif)

This is the validation back-end for my TI-30Xa emulator. It is constantly pressing buttons on a TI-30Xa calculator and recording what the LCD shows. The results get stored in an SQLite database. The database is too big to be stored on github, but you can download a CSV from [https://home.aldenbradford.com:58086/](https://home.aldenbradford.com:58086/). In addition, whenever anyone uses the calculator at [https://aldenbradford.com/calculator_emulator/](https://aldenbradford.com/calculator_emulator/) the sequence of button presses is sent to Xanthippe to be tested. It will show up in the database the following day.

For more information about this project, [please see my blog](https://aldenbradford.com/tag/xanthippe.html).
