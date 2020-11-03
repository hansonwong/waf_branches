function main()

    --m.log(1, "Hello world!");

    local filename = m.getvar("FILES_TMPNAMES");
    local ocr_file = filename .. "-ocr"
    cmd = "tesseract "..filename.." "..ocr_file.." -l chi_sim"
    fp = io.popen(cmd)

    text = ""

    if fp ~= nil then
    	fp:close()
    	fp = io.open(ocr_file..".txt")
    	if fp then
		    text = fp:read("*a")
		    fp:close()
		    -- m.log(1, "========== " .. text);
		    m.setvar("tx.ocr_text", text);
		    -- m.setvar("tx.if_feifa_pic", 2);
		end
	end


    return nil;
end
