Click on the green flag, enter the inputs provided in the “testing examples” to
see the expected output of your program.

{iframe link="https://scratch.mit.edu/projects/embed/148425996/?autostart=false"}

{panel type="help" title="Recommended blocks"}

```scratch:split:random
when green flag clicked

ask [Please enter a black or white square (B for black or W for white):] and wait

say (black cards total)
```

```scratch:split:random
set [black cards total v] to [0]

change [black cards total v] by (1)
```

```scratch:split:random
repeat (5)
end

if <(answer) = [B]> then
end
```

{panel end}
