function sparallel
{
  command /srv/sw/parallel/20151122/bin/parallel `module list -l 2>&1 |tail -n+3 |awk '{print $1}' |sed 's%^/%%' |parallel -k module show '2>&1' |grep prepend-path |awk '{print $2}' |sort |uniq |tr '\n' ' ' |sed 's/ $//' |sed 's/^/ /' |sed 's/ / --env /g'` $@
}
