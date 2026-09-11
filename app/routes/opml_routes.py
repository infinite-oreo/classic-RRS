from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from .. import db, opml

bp = Blueprint("opml", __name__, url_prefix="/opml")


@bp.route("/export")
def export():
    conn = db.get_db()
    xml_bytes = opml.export_opml(conn)
    return Response(
        xml_bytes,
        mimetype="text/x-opml",
        headers={"Content-Disposition": "attachment; filename=subscriptions.opml"},
    )


@bp.route("/import", methods=["GET", "POST"])
def import_view():
    if request.method == "POST":
        file = request.files.get("opml_file")
        if file and file.filename:
            conn = db.get_db()
            imported, skipped = opml.import_opml(conn, file.read())
            flash(f"成功导入 {imported} 个订阅源,跳过 {skipped} 个重复")
        return redirect(url_for("feeds.index"))
    return render_template("opml_import.html")
