#!/usr/bin/ruby
#
# Rename one or more files or directories starting with "nts_d"
# followed by a MAC address, so that they include Crowbar node
# aliases.

require "fileutils"
require "pathname"
require "pp"
require "yaml"

def get_new_filename(path, mac_to_host)
  filename = path.basename

  mac_to_host.each do |mac, host|
    if filename.to_s =~ /#{mac}/i
      return path.dirname + filename.sub(mac, host + "_" + mac)
    end
  end

  return nil
end

def progress(msg)
  $stderr.puts "# " + msg
end

def rename_all(paths, mac_to_host)
  macs_regexp = Regexp.new(mac_to_host.keys.join("|"))

  paths.map do |path|
    next unless File.exist? path
    path = Pathname.new(path)
    #next unless path.basename.to_s =~ /^nts_d((?<byte>[0-9a-f]{2})(-\g<byte>){5})_/
    #mac = $1

    new_name = get_new_filename(path, mac_to_host)
    if new_name
      path.rename new_name
    else
      puts "leaving #{path} as is"
    end
  end.compact
end

def main
  if ARGV.size < 2
    abort "Usage: #$0 MACS-YAML FILE [...]"
  end

  macs_file = ARGV.shift

  mac_to_host = YAML.load_file(macs_file)

  rename_all(ARGV, mac_to_host)
end

main
