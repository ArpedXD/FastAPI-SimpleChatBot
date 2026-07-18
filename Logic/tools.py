
class Tools:
    def cursorRequest(request):
        db = request.app.state.db
        cursor = db.cursor(buffered=True)
        return cursor
    
    def connectionCommit(request):
        return request.app.state.db.commit()