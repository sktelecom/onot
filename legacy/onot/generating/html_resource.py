#!/usr/bin/env python3

DOCTYPE = """
<!DOCTYPE html>"""
XMLNS = """
<html lang="en">"""
HEAD = """
<head>
  <meta charset="UTF-8">
  <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" />
  <meta name='title' content='OSS Notice'>
    <title>OSS Notice</title>"""
STYLE_CSS = """
        <style>
        body, th, td, div, textarea, pre {
          font-family: 'Malgun Gothic','맑은 고딕','Apple SD Gothic Neo','돋움',dotum,sans-serif,Arial;
        }
        a,a:visited,a:active { color: #0969da ;text-decoration: none}
        a:hover { color:dodgerblue ; text-decoration: underline}
        .notice { position: relative;}
        h2 {
          color:#ffffff;
          font-size:26px;
          text-align:center;
          position: relative;
          -webkit-box-sizing: border-box;
          box-sizing: border-box;
        }
        h3 {
          /*color:#ea002c;*/
          font-size:22px;
          color:#000;
        }
        h4 {
          font-size:18px;
          font-weight: 600;
        }
        h4 a {
          font-size:14px;
          display:inline-block;
          /*background:#fae100;*/
          border: 1px solid #8a8a8a;
          padding:4px 12px;
          border-radius: 16px;
          margin:4px;
        }
        h4 a,a:visited { color: #0969da ;text-decoration: none}
        h4 a:hover , h4 a:active { color:#ffffff ; text-decoration: none}
        h4 a:hover{
          background:#0969da;
          cursor:pointer;
        }
        .article {
          color:#777777;
          font-weight: 400;
          font-size:14px;
          line-height:160%;
          margin-bottom:44px;
        }
        .tt_wrap {
          padding:24px;
          background-color:#000000;
        }
        .tt_desc {
          color:#202021;
          font-size:16px;
          padding:24px 36px;
          line-height:150%;
        }
        .tt_line {border-top: #dcdcdc solid 1px;font-size: 1px;}
        .tt_licenses, .tt_sc {
          padding: 24px;
        }
        .tt_licenses .license {
          border-top: 1px solid #000;
        }
        .no_data {
          text-align:center;
          padding: 30px !important;
        }
        .tt_sc {
          background-color:#eeeeee;
        }
        .tt_sc .sc_title {
          color:#202021;
          font-size:22px;
          font-weight: 600;
        }
        .sc_desc , .sc_contact {
          font-size:14px;
          line-height:150%;
          margin-top:25px;
        }
        .tt_components {
          position: relative;
          overflow: hidden;
          margin: 0 auto;
          padding: 24px;
        }
        .tt_components table {
          display: table;
          padding: 24px;
          width: 100%;
          border-collapse: collapse;
          border-spacing: 0;
          border-top: 2px solid #000;
          border-bottom: 1px solid #000;
        }
        .tt_components thead th {
          font-size:16px;
          text-align:left;
          border-left: 1px solid #eaecf0;
          border-bottom:1px solid #eaecf0;
        }
        .tt_components td {
          border-bottom:#eaecf0 solid 1px;
          border-left: 1px solid #eaecf0;
          font-size:14px;
        }
        .tt_components tr td:first-child , .tt_components thead th:first-child {
          border-left:none;
        }
        .tt_components tr:last-child td {
          border-bottom:none;
        }
        .tt_components table tbody tr td {
          border-bottom: 1px solid #efefef;
        }
        .tt_components table thead tr th,
        .tt_components table tbody tr td {
          padding: 12px 20px;
          font-size: 16px;
          line-height: 22px;
        }
        @media screen and (max-width: 990px) {
          .tt_components table col {
            width: 100% !important;
          }
          .tt_components table thead {
            display: none;
          }
          .tt_components table tbody tr {
            border-bottom: 1px solid #efefef;
          }
          .tt_components td {
            border-left:none;
          }
          .tt_components table tbody tr td {
            width: 100%;
            display: flex;
            margin-bottom: 2px;
            padding: 5px;
            border-bottom: none;
            font-size: 14px;
            line-height: 18px;
          }
          .tt_components table tbody tr td:first-child,
          .tt_components table tbody tr th:first-child {
            padding-top: 16px;
          }
          .tt_components table tbody tr td:last-child,
          .tt_components table tbody tr th:last-child {
            padding-bottom: 15px;
          }
          .tt_components table tbody tr td:before {
            margin-right: 12px;
            -webkit-box-flex: 0;
            -ms-flex: 0 0 100px;
            flex: 0 0 100px;
            font-size:16px;
            font-weight: 800;
            content: attr(data-label);
          }
        }
      </style>
    </head>"""
BODY_TABLE_1 = """
    <body>
    <div class="notice">
      <div class="tt_wrap">"""
BODY_TABLE_2 = """
      </div>
      <div class="tt_desc">"""
COMPONENT_TITLE = """
       </div>
      <div class="tt_line"></div>
       <div class="tt_components">
        <h3>components</h3>
        <table>
          <colgroup>
            <col style="width:20%">
            <col style="width:30%">
            <col style="width:50%">
          </colgroup>
        <thead>
        <tr>
          <th>Name</th>
          <th>License</th>
          <th>Copyright</th>
        </tr>
        </thead>
        <tbody>"""
TABLE_ROW_NO = """
        <tr>
          <td colspan="3" class="no_data">
            No Components
          </td>
        </tr>"""
TABLE_CLOSE = """
        </tbody>
        </table>
    </div>
"""
LICENSE_TITLE = """
    <div class="tt_licenses">
        <h3>licenses</h3>
"""
LICENSE_TABLE_CLOSE = """</div>"""
WRITTEN_OFFER_TITLE = """
    <div class="tt_line"></div>
    <div class="tt_sc">
        <div class="sc_title">Offer of Source Code</div>
        <div class="sc_desc">
"""
WRITTEN_OFFER_CLOSE = """
        </div>
        <div class="sc_contact">
"""
FOOTER = """
        </div>
    </div>
</div>
</body>
"""
