#!/usr/bin/env bash

_bob_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _BOB_COMPLETE=complete $1 ) )
    return 0
}

complete -F _bob_completion -o default bob;
