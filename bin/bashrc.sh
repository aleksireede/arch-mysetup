# ~/.bashrc

# Exit if shell is not interactive
[[ $- != *i* ]] && return

# -----------------------------------------------------------------------------
# Starship prompt
# -----------------------------------------------------------------------------

if [[ -x /usr/bin/starship ]]; then
    source <(/usr/bin/starship init bash)
fi

# -----------------------------------------------------------------------------
# PATH
# -----------------------------------------------------------------------------

export PATH="$PATH:$HOME/.local/bin"

# -----------------------------------------------------------------------------
# Better replacements
# -----------------------------------------------------------------------------

if command -v eza >/dev/null; then
    alias ls='eza --all --long --group-directories-first --icons=auto'
    alias la='eza -a --group-directories-first --icons=auto'
    alias ll='eza -l --group-directories-first --icons=auto'
    alias lt='eza -aT --group-directories-first --icons=auto'
    alias l.='eza -ald .* --icons=auto'
fi

if command -v bat >/dev/null; then
    alias cat='bat --style=header,snip,changes'
fi

if [[ ! -x /usr/bin/yay && -x /usr/bin/paru ]]; then
    alias yay='paru'
fi

alias grep='ugrep --color=auto'
alias fgrep='ugrep -F --color=auto'
alias egrep='ugrep -E --color=auto'

# -----------------------------------------------------------------------------
# Navigation
# -----------------------------------------------------------------------------

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ......='cd ../../../../..'

mkcd() {
    mkdir -p "$1" && cd "$1"
}

# -----------------------------------------------------------------------------
# File utilities
# -----------------------------------------------------------------------------

alias cp='cp -iv'
alias mv='mv -iv'
alias mkdir='mkdir -pv'

alias df='df -h'
alias du='du -h'
alias free='free -h'
alias cls='clear'

alias dir='dir --color=auto'
alias vdir='vdir --color=auto'

tarnow() {
    tar -acf "$1.tar.gz" "${@:2}"
}

alias untar='tar -xf'

extract() {
    [[ ! -f "$1" ]] && {
        echo "File not found."
        return 1
    }

    case "$1" in
        *.tar.bz2) tar xjf "$1" ;;
        *.tar.gz) tar xzf "$1" ;;
        *.tar.xz) tar xJf "$1" ;;
        *.tar.zst) tar --zstd -xf "$1" ;;
        *.tar) tar xf "$1" ;;
        *.zip) unzip "$1" ;;
        *.7z) 7z x "$1" ;;
        *.rar) unrar x "$1" ;;
        *) echo "Unsupported archive." ;;
    esac
}

# -----------------------------------------------------------------------------
# Package management
# -----------------------------------------------------------------------------

alias grubup='sudo update-grub'
alias upd='garuda-update'

fixpacman() {
    sudo rm -f /var/lib/pacman/db.lck
}

cleanup() {
    local orphans
    orphans=$(pacman -Qtdq)

    if [[ -n "$orphans" ]]; then
        sudo pacman -Rns "$orphans"
    else
        echo "No orphan packages."
    fi
}

alias rmpkg='sudo pacman -Rdd'

# -----------------------------------------------------------------------------
# Reflector
# -----------------------------------------------------------------------------

alias mirror='sudo reflector \
    --country Finland,Sweden,Estonia,Germany \
    --protocol https \
    --latest 20 \
    --sort rate \
    --save /etc/pacman.d/mirrorlist'

alias mirrorfi='sudo reflector \
    --country Finland \
    --protocol https \
    --latest 10 \
    --sort rate \
    --save /etc/pacman.d/mirrorlist'

alias mirrorworld='sudo reflector \
    --protocol https \
    --latest 30 \
    --sort rate \
    --save /etc/pacman.d/mirrorlist'

# -----------------------------------------------------------------------------
# System information
# -----------------------------------------------------------------------------

alias hw='hwinfo --short'
alias ip='ip -color'

alias psmem='ps auxf | sort -nr -k4'
alias psmem10='ps auxf | sort -nr -k4 | head'

alias jctl='journalctl -p3 -xb'

alias big="expac -H M '%m\t%n' | sort -h | nl"
alias gitpkg='pacman -Q | grep "\-git" | wc -l'
alias rip="expac --timefmt='%Y-%m-%d %T' '%l\t%n %v' | sort | tail -200 | nl"

# -----------------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------------

alias apt='man pacman'
alias apt-get='man pacman'
alias please='sudo'
alias tb='nc termbin.com 9999'
alias helpme='cht.sh --shell'
alias pacdiff='sudo -H DIFFPROG=meld pacdiff'

# -----------------------------------------------------------------------------
# Personal configuration
# -----------------------------------------------------------------------------

if [ -f ~/.bash_extra ]; then
. ~/.bash_extra
fi
