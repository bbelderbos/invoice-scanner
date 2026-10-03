Output demo/review.gif
Output demo/review.mp4

Set Shell "bash"
Set FontSize 16
Set Width 1300
Set Height 760
Set Padding 20
Set TypingSpeed 40ms
Set Theme "Catppuccin Mocha"

Hide
Type "source .venv/bin/activate && export XDG_DATA_HOME=$(mktemp -d) PS1='$ ' && clear"
Enter
Show

Type "invoice-scan samples/cowork_ambiguous.pdf --review --categories office,coworking > expense.json"
Sleep 500ms
Enter
# the ~8s model call is cut from the recording
Hide
Wait@60s /date \[/
Show
Sleep 4s

# receipt was April 3rd, not March 4th
Type "2026-04-03"
Sleep 800ms
Enter
Wait /payment_method \[/
Sleep 1.5s
Enter
Wait /currency \[/
Sleep 1.5s
Enter
Wait /Field to edit/
Sleep 3s

# fix a field the model was confident about
Type "description"
Enter
Wait /description \[/
Type "Hot desk day pass x2 (team offsite)"
Sleep 800ms
Enter
Wait /Field to edit/
Sleep 1s
Enter
Sleep 1s

Type "clear && jq '{date, description, currency, payment_method}' expense.json"
Enter
Sleep 3s

Type "invoice-scan --stats"
Enter
Sleep 5s
