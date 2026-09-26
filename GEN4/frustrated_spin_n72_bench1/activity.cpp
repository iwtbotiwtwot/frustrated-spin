#include <cupti.h>
#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <vector>
#include <mutex>
#include <ctime>
struct Row {uint64_t start,end;uint32_t device,stream;};
static std::mutex guard;static std::vector<Row> rows;static size_t dropped=0;static int64_t offset=0;
static void CUPTIAPI request(uint8_t **buffer,size_t *size,size_t *maximum){*size=4*1024*1024;*buffer=(uint8_t*)std::malloc(*size);*maximum=0;}
static void CUPTIAPI complete(CUcontext context,uint32_t stream,uint8_t *buffer,size_t size,size_t valid){
 CUpti_Activity *record=nullptr;std::lock_guard<std::mutex> lock(guard);
 while(cuptiActivityGetNextRecord(buffer,valid,&record)==CUPTI_SUCCESS){
  if(record->kind==CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL){auto *k=(CUpti_ActivityKernel9*)record;rows.push_back({k->start,k->end,k->deviceId,k->streamId});}
 }
 size_t n=0;cuptiActivityGetNumDroppedRecords(context,stream,&n);dropped+=n;std::free(buffer);
}
extern "C" int trace_begin(){
 uint64_t ts=0;timespec mono;cuptiGetTimestamp(&ts);clock_gettime(CLOCK_MONOTONIC,&mono);offset=int64_t(mono.tv_sec)*1000000000+mono.tv_nsec-int64_t(ts);
 auto r=cuptiActivityRegisterCallbacks(request,complete);if(r!=CUPTI_SUCCESS)return int(r);
 return int(cuptiActivityEnable(CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL));
}
extern "C" int trace_end(const char *path){
 auto r=cuptiActivityFlushAll(0);cuptiActivityDisable(CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL);
 std::lock_guard<std::mutex> lock(guard);FILE *f=std::fopen(path,"w");if(!f)return -1;
 std::fprintf(f,"{\"offset_ns\":%lld,\"dropped\":%zu,\"records\":%zu}\n",(long long)offset,dropped,rows.size());
 for(auto &x:rows)std::fprintf(f,"%llu,%llu,%u,%u\n",(unsigned long long)x.start,(unsigned long long)x.end,x.device,x.stream);
 std::fclose(f);return int(r);
}
