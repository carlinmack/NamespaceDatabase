# Format of Wiki-dump XML files

All XML dump files of the format `enwiki-20200101-pages-meta-history1.xml-pXXXpXXX` have the following structure, with lines that are `...` being repetitive or omitted content.

You can view the edit history for the first listed page in this example [here](https://en.wikipedia.org/w/index.php?title=AccessibleComputing&offset=&limit=500&action=history) and the second page [here (15:00, February 25, 2002)](https://en.wikipedia.org/w/index.php?title=Anarchism&dir=prev&limit=20&action=history)

```XML
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd"
    version="0.10" xml:lang="en">
    <siteinfo>
        <sitename>Wikipedia</sitename>
        <dbname>enwiki</dbname>
        <base>https://en.wikipedia.org/wiki/Main_Page</base>
        <generator>MediaWiki 1.35.0-wmf.11</generator>
        <case>first-letter</case>
        <namespaces>
            <namespace key="-2" case="first-letter">Media</namespace>
            <namespace key="-1" case="first-letter">Special</namespace>
            <namespace key="0" case="first-letter" />
            <namespace key="1" case="first-letter">Talk</namespace>
            <namespace key="2" case="first-letter">User</namespace>
            <namespace key="3" case="first-letter">User talk</namespace>
            ...
            <namespace key="2303" case="case-sensitive">Gadget
                definition talk</namespace>
        </namespaces>
    </siteinfo>
    <page>
        <title>AccessibleComputing</title>
        <ns>0</ns>
        <id>10</id>
        <redirect title="Computer accessibility" />
        <revision>
            <id>233192</id>
            <timestamp>2001-01-21T02:12:21Z</timestamp>
            <contributor>
                <username>RoseParks</username>
                <id>99</id>
            </contributor>
            <comment>*</comment>
            <model>wikitext</model>
            <format>text/x-wiki</format>
            <text xml:space="preserve">This subject covers

* AssistiveTechnology

* AccessibleSoftware

* AccessibleWeb

* LegalIssuesInAccessibleComputing

            </text>
            <sha1>8kul9tlwjm9oxgvqzbwuegt9b2830vw</sha1>
        </revision>
        <revision>
            <id>862220</id>
            <parentid>233192</parentid>
            <timestamp>2002-02-25T15:43:11Z</timestamp>
            <contributor>
                <username>Conversion script</username>
                <id>1226483</id>
            </contributor>
            <minor />
            <comment>Automated conversion</comment>
            <model>wikitext</model>
            <format>text/x-wiki</format>
            <text xml:space="preserve">#REDIRECT [[Accessible Computing]]
            </text>
            <sha1>i8pwco22fwt12yp12x29wc065ded2bh</sha1>
        </revision>
        <revision>
            ...
        </revision>
        ...
        <revision>
            <id>854851586</id>
            <parentid>834079434</parentid>
            <timestamp>2018-08-14T06:47:24Z</timestamp>
            <contributor>
                <username>Godsy</username>
                <id>23257138</id>
            </contributor>
            <comment>remove from category for seeking instructions on rcats</comment>
            <model>wikitext</model>
            <format>text/x-wiki</format>
            <text xml:space="preserve">#REDIRECT [[Computer accessibility]]
                {{R from move}}
                {{R from CamelCase}}
                {{R unprintworthy}}</text>
            <sha1>42l0cvblwtb4nnupxm6wo000d27t6kf</sha1>
        </revision>
    </page>
    <page>
        <title>Anarchism</title>
        <ns>0</ns>
        <id>12</id>
        <revision>
            <id>18201</id>
            <parentid>332419362</parentid>
            <timestamp>2002-02-25T15:00:22Z</timestamp>
            <contributor>
                <username>Conversion script</username>
                <id>12  26483</id>
            </contributor>
            <minor />
            <comment>Automated conversion</comment>
            <model>wikitext</model>
            <format>text/x-wiki</format>
            <text xml:space="preserve">''Anarchism'' is the political theory that advocates the abolition of all forms of government. The word anarchism derives from Greek roots &lt;i&gt;an&lt;/i&gt; (no) and &lt;i&gt;archos&lt;/i&gt; (ruler).
            ...
            </text>
            <sha1>07sqam7073877kptdznnip3viznphpy</sha1>
        </revision>
        <revision>
        ...
        </revision>
        ...
    </page>
    ...
</mediawiki>
```