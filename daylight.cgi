#!/usr/local/bin/ruby

# interpolate to find morning/evening and then report length of day between.

puts "Access-Control-Allow-Origin: *"
puts "Content-type: text/plain"
puts ""

v0 = 0
t0 = 0
tm = te = 0
File.readlines('results/a2010/history.txt').each do |line|
  t,v = line.split("\t")
  t1 = t.to_i
  v1 = v.to_f
  if v0 < 50 && v1 >= 50
    dt = t1 - t0
    dv = v1 - v0
    p = (50 - v0) / dv
    tm = t0 + p * dt
    # puts "#{t} #{v1} #{tm}  #{p}"
  end
  if v0 > 50 && v1 <= 50
    dt = t1 - t0
    dv = v1 - v0
    p = (50 - v0) / dv
    te = t0 + p * dt
    l = (te-tm)/(60*60)
    if l<18 && l>6
      puts "#{te}\t#{l}\t#{'|' * (6*l)}"
    elsif l>24
      puts "#{te}\t#{l}"
    end
  end
  t0 = t1
  v0 = v1
end

