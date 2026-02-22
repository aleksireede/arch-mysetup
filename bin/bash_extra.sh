alias localip="ifconfig | grep inet"
alias extip='echo $(dig -4 TXT +short o-o.myaddr.l.google.com @ns1.google.com)'

alias neofetch="fastfetch | lolcat"
alias fastfetch="fastfetch | lolcat"

alias path='echo -e "${PATH//:/\\n}"'
alias cd..="cd .."
alias ..="cd .."
alias ...="cd ../../../"
alias gh="history|grep"
mnt() {
    mount | awk -F' ' '{ printf "%s\t%s\n",$1,$3; }' | column -t | grep '^/dev/' | sort
}

alias listaur="paru -Qemq | lolcat"
alias listpkg="paru -Qenq | lolcat"
alias update="paru -Suy --skipreview --quiet --needed --color always"
alias install="paru -S --skipreview --quiet --needed --color always"
alias remove="paru -Rns --quiet --color always"

export QT_PLUGIN_PATH=/usr/lib/qt/plugins
export QT_QPA_PLATFORM=wayland
export EDITOR=nano
export XDG_RUNTIME_DIR="/run/user/$UID"
export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

clear && fortune | cowsay -f tux | lolcat
