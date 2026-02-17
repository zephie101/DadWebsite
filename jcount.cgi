#!/usr/local/bin/perl

# jcount.cgi once-simple counter script for Java front end -- Paul Lutus lutusp@arachnoid.com

# version date: 10/9/1998

print "Content-type:text/plain\n\n";


# NT bases addressing on site root, UNIX bases it on the actual directory of the script

# So, ...

$relPath = ""; # assume this is undefined

if($ENV{'PATH_INFO'}) { # this only exists on NT servers
		$relPath = $ENV{'PATH_INFO'};
	$relPath =~ s/(^\/)(.*)(\/.*)/$2/; # isolate path to counter directory
	$relPath .= "/";
}

$filename = "defaultfile";
$callinghost = "";
$host = "";

if($ENV{'REQUEST_METHOD'}) {
		if ($ENV{'REQUEST_METHOD'} eq "GET") {
			if($ENV{'QUERY_STRING'}) {
				$buffer = $ENV{'QUERY_STRING'}; # get the file name from counter.cgi?ownername construct
			@buffer = split(/&/,$buffer);
		}
		else { # no query string
			exitTest(1,0);
		}
	}
	elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
			if($ENV{'CONTENT_LENGTH'}) {
				read(STDIN,$buffer,$ENV{'CONTENT_LENGTH'});
			$buffer =~ s/\r//g; # a precaution
			@buffer = split(/\n/,$buffer);
		}
		else { # no content length
			exitTest(1,0);
		}
	}
	
	foreach $pair (@buffer) {
		$pair =~ tr/+/ /;
		$pair =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
		($name,$value) = split(/=/,$pair);
		$name =~ s/[&;`'|*?~<>^{}\[\]\$\n\r]//g; # filter metacharacters
			$value =~ s/[&;`'|*?~<>^{}\[\]\$\n\r]//g; # filter metacharacters
			$FORM{$name} = $value;
	}
	
	$filename = $FORM{'counter'}; # get the name of the counter file
	$callinghost = $FORM{'host'}; # get the name of the source site
	$host = $ENV{'HTTP_HOST'}; # get the name of the local server
	
	$callinghost =~ s/^http:\/\/([\w|\.|-]+)\/.+$/$1/; # isolate host name
}

if (($callinghost ne $host) # if caller is not on this server
		|| (length($filename) == 0) # or if these values have not been changed
|| (length($callinghost) == 0))
{
	exitTest(1,0); # force exit condition
}

$countpath = $relPath . "data/$filename";

$lockpath = "$countpath\.lock";

$count = 0;

# this script has been resetting valid counters, so do a better check

$waitcount = 0;

while((!(-e $countpath)) && ($waitcount++ < 32)) { # while file appears not to exist
	sleep(2);
}

if($waitcount >= 32) { # no file (?)
	open(DATA, ">$countpath");
	print DATA "1";
	close DATA;
}

# while lock file exists, or not old, wait

$ok = 0;
$waitcount = 0;

while((!$ok) && ($waitcount++ < 10)) {
	@statData = stat($lockpath);
	$mtime = $statData[9];
	$exists = $#statData > -1;
		if(!$exists) {
			$mtime = time();
	}
	$tt = time();
	$ok = ((!$exists) || ($mtime < ($tt-3600))); # OK if the lock file is zero-length or over an hour old
	if(!$ok) {
		sleep(2);
	}
}

exitTest($waitcount,10);

open(LOCK,">$lockpath"); # create zero length lock file
close LOCK;

# wait while counter not writable

$waitcount = 0;

while((!(-w $countpath)) && ($waitcount++ < 10))
{
	sleep(2);
}

if ($waitcount < 10) { # if OK to access counter
	if(open (DATA,"+<$countpath")) { # if file is accessible and opened
		$count = <DATA>;
		if($count > 0) { # my counters are never zero - this is a read success test
			$count++;
			seek(DATA,0,0); # reset to beginning of file
			print DATA "$count\n";
		}
		close DATA;
	}
}

unlink($lockpath); # delete the lock file

# finally ...

print "$count\n";

exit;

sub exitTest {
	if($_[0] >= $_[1]) { # if wait counter >= max wait time
		print("0\n");
		exit;
	}
}

sub trace {
	# print("$_[0]\n");
	local $path = $relPath . "trace.txt";
	open(TRACE,">>$path");
	print TRACE "$_[0]\n";
	close TRACE;
}
