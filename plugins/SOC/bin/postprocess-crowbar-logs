#!/usr/bin/ruby
#
# Post-process a bunch of log files described in a YAML file,
# performing substitutions given in another YAML file on both the
# contents and the names of the newly-written files.
#
# The substitutions are intended to make the filenames and their
# contents easier to read from a logfile reader such as lnav.  One
# common use case is to substitute Crowbar hostnames (which are based
# on MAC addresses) for corresponding host aliases.
#
# The names of the processed versions of the log files are output
# to STDOUT, so that they can be passed to the logfile reader.
#
# Once a processed file is generated it will not be overwritten.

require "fileutils"
require "pathname"
require "pp"
require "yaml"

PROCESSED_SUFFIX = ".p"

# Make filename as concise and informative as possible for use with
# https://github.com/tstack/lnav/pull/372
def get_processed_filename(path, mac_to_host)
  path = Pathname.new(path)
  dir = path.dirname
  filename = File.basename path
  filename.sub! /(neutron-)?openvswitch/, "OVS"
  filename.sub! /(neutron-)?openvswitch/, "OVS"

  mac_to_host.each do |mac, host|
    if filename.to_s =~ /#{mac}/i
      filename.sub!(mac, host)
      return dir + (filename + PROCESSED_SUFFIX)
    end

    if path.to_s =~ /#{mac}/i
      return dir + ("#{host}-#{filename}" + PROCESSED_SUFFIX)
    end
  end

  path.to_s + PROCESSED_SUFFIX
end

def needs_processing(file, processed_name)
  return true unless File.exist? processed_name
  return ! FileUtils.uptodate?(processed_name, [file.to_s])
end

def progress(msg)
  $stderr.puts "# " + msg
end

def preprocess_all(files, mac_to_host, addr_to_host)
  replacement_strings = mac_to_host.keys + addr_to_host.keys
  regexp = Regexp.new(replacement_strings.join("|"))

  files.map do |file|
    if ! File.file? file.to_s
      progress "Skipping non-file #{file}"
      next
    end

    next if file.to_s.end_with? PROCESSED_SUFFIX

    processed_name = get_processed_filename(file, mac_to_host)
    if needs_processing(file, processed_name)
      progress "Pre-processing #{file} ..."
      preprocess(file, processed_name, regexp, mac_to_host, addr_to_host)
    end

    puts processed_name.to_s
  end.compact
end

def preprocess(in_file, out_file, regexp, mac_to_host, addr_to_host)
  progress "  -> #{out_file}"
  File.open(out_file, "w") do |out|
    File.new(in_file, encoding: Encoding::ASCII_8BIT).each do |line|
      new_line = line.gsub(macs_regexp) do |m|
        if mac_to_host[$&]
          mac_to_host[$&]
        elsif addr_to_host[$&]
          addr_to_host[$&]
        else
          raise "Didn't have entry for $& as MAC or IP address"
          exit
        end
      end
      out.puts new_line
    end
  end
end

def logfiles_from_yaml(yaml)
  file_globs = YAML.load_file(yaml)

  return glob(file_globs.values) if ARGV.empty?

  ARGV.map do |arg|
    if File.exist? arg
      arg
    elsif file_globs.has_key?(arg)
      glob(file_globs[arg])
    else
      abort "#{arg} is neither a file nor glob category"
      nil
    end
  end.flatten.compact
end

# Takes an Array of globs and returns an Array of files
def glob(globs)
  globs.map { |g| Pathname.glob g }.flatten.map(&:to_s).uniq
end

def main
  if ARGV.size < 2
    abort "Usage: #$0 LOG-YAML MACS-YAML IP-ADDRS-YAML [LOG-SECTION ...]"
  end

  logfiles_config = ARGV.shift
  macs_file = ARGV.shift
  addr_file = ARGV.shift

  logfiles = logfiles_from_yaml(logfiles_config)
  mac_to_host = YAML.load_file(macs_file)
  addr_to_host = YAML.load_file(addr_file)

  preprocess_all(logfiles, mac_to_host, addr_to_host)
end

main
