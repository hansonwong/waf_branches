<?php
namespace app\logic\common;


class CvsHelper
{
    protected $exportRow = 0, $fopenObj = null;

    /**
     * 导出文件声明
     * @param $fileName
     */
    public function exportFileName($fileName){
        header('Content-Type: application/vnd.ms-excel');
        header("Content-Disposition: attachment;filename=\"".iconv('utf-8', 'gbk', $fileName).".csv\"");
        header('Cache-Control: max-age=0');

        // 打开PHP文件句柄，php://output 表示直接输出到浏览器
        $this->fopenObj = fopen('php://output', 'a');
    }

    /**
     * 导出表头
     * @param $head
     */
    public function exportHead($head){
        foreach ($head as $i => $v)
            $head[$i] = iconv('utf-8', 'gbk', $v);// CSV的Excel支持GBK编码，一定要转换，否则乱码

        fputcsv($this->fopenObj, $head);// 将数据通过fputcsv写到文件句柄
    }

    /**
     * 导出表体单项
     * @param $item
     * @param $exportRowFlushCount
     */
    public function exportBodyItem($item, $exportCloumn = [], $exportRowFlushCount = 50){
        $exportRowFlushCount = intval($exportRowFlushCount);
        if ($exportRowFlushCount == $this->exportRow++) { //刷新一下输出buffer，防止由于数据过多造成问题
            ob_flush();
            flush();
            $this->exportRow = 0;
        }

        if([] == $exportCloumn){
            foreach ($item as $k => $v)
                $item[$k] = iconv('utf-8', 'gbk', $v);
            fputcsv($this->fopenObj, $item);
        } else {
            if(is_array($exportCloumn)){
                $data = [];
                foreach ($exportCloumn as $key)
                    $data[] = iconv('utf-8', 'gbk', $item[$key]);
                fputcsv($this->fopenObj, $data);
            }
        }
    }

    /**
     * 导出表体所有
     * @param $item
     * @param $exportRowFlushCount
     */
    public function exportBody($data, $exportCloumn = [], $exportRowFlushCount = 50){
        foreach ($data as $item){
            $this->exportBodyItem($item, $exportCloumn, $exportRowFlushCount);
        }
    }

    public function importAndGetData($file, $hasHead = true){
        $handle=fopen($file,"r");
        $i = $hasHead ? 0 : 1;
        $items = [];
        while($data=fgetcsv($handle,10000,",")) {
            if(0 == $i++) continue;
            $items[] = array_map(function($v){
                return trim(iconv('gbk', 'utf-8', $v));
            }, $data);
        }
        return $items;
    }
}