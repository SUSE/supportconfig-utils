
REGEXPS = {
  state: [
    /online/,
    /offline/,
    /standby/,
    /maintenance/,
    /reboot/,
    /revived/,
    /[^-]timeout/,
  ],
  corosync: [
    /TOTEM.*Retransmit/,
  ],
  pacemaker: [
    /started/,
    /stopped/,
    /stonith/,
    /fence/,
    /fencing/,
  ],
  updates: [
    /zypper.*/
  ]
}

regexps = [:state, :corosync, :pacemaker, :updates].map { |s| REGEXPS[s] }

puts "Suggested copy'n'paste for a useful search:\n\n"
puts "/" + regexps.flatten.map { |re| re.source }.join("|")

    #"-c", ":highlight #{regexps.join ''}",
    #"-c", ":highlight #{regexps.join ''}",
